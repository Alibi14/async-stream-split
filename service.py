import math
import asyncio

from aiobotocore.session import get_session
from fastapi import UploadFile, File

import settings

part_info = {
    'Parts': []
}

# Надо лочить и сохранять в объекте один раз, чтобы каждый раз не возвращаться в event_loop
file_shared_lock = asyncio.Lock()


async def upload_chunk(
        client,
        file,
        upload_id,
        chunk_number,
        source_size,
        key
):
    offset = chunk_number * int(settings.CHUNK_SIZE)
    remaining_bytes = source_size - offset
    bytes_to_read = min([int(settings.CHUNK_SIZE), remaining_bytes])
    part_number = chunk_number + 1

    async with file_shared_lock:
        # почему-то если не лочить в контексте то другая корутина делает дополнительный seek(),
        # что не является thread-safe операцией
        await file.seek(offset)
        chunk = await file.read(bytes_to_read)

    resp = await client.upload_part(
        Bucket=settings.AWS_S3_BUCKET_NAME,
        Body=chunk,
        UploadId=upload_id,
        PartNumber=part_number,
        Key=key
    )

    global part_info
    part_info['Parts'].append(
        {
            'PartNumber': part_number,
            'ETag': resp['ETag']
        }
    )


async def upload_file(
    file: UploadFile = File(...)
):
    bytes_per_chunk = int(settings.CHUNK_SIZE)
    filename = file.filename

    # Создание сессии
    session = get_session()
    async with session.create_client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_secret_access_key=settings.AWS_S3_SECRET_KEY,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID
    ) as client:

        file_size = file.size
        chunks_count = int(math.ceil(file_size / float(bytes_per_chunk)))

        mpu = await client.create_multipart_upload(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=filename
        )

        tasks = []
        # Собираем в массив корутины чтобы дальше они запускались как конкурентные таски
        for chunk_number in range(chunks_count):
            tasks.append(
                upload_chunk(
                    client=client,
                    file=file,
                    chunk_number=chunk_number,
                    key=filename,
                    upload_id=mpu['UploadId'],
                    source_size=file_size
                )
            )

        await asyncio.gather(*tasks)  # run concurrently

        # Далее информация о парционно загруженных элементах
        list_parts_resp = await client.list_parts(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=filename,
            UploadId=mpu['UploadId']
        )

        # т.к. файлы были загружены конкурентно, надо их отсортировать чтобы закончить загрузку
        part_list = sorted(part_info['Parts'], key=lambda k: k['PartNumber'])
        part_info['Parts'] = part_list

        is_finished = len(list_parts_resp['Parts']) == chunks_count

        # если количество чанков равно количеству загруженных элементов, заканчиваем, иначе - сброс
        if is_finished:
            await client.complete_multipart_upload(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=filename,
                UploadId=mpu['UploadId'],
                MultipartUpload=part_info
            )
        else:
            await client.abort_multipart_upload(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=filename,
                UploadId=mpu['UploadId']
            )
    return {'filename': filename}
