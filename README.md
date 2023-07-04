# uchetkztodo

Добавил .env файл для удобства, в реальном проекте я бы воздержался
Так же раскидал бы по папкам, но так же для удобства оставил так.

Использовал minio для s3. С докером были проблемы, так что вот инстркуция как быстро скачать:

wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20230629051228.0.0_amd64.deb -O minio.deb

sudo dpkg -i minio.deb

Далее создаете папку и запускаете 

mkdir ~/minio

minio server ~/minio --console-address :9090

По дефолту будет на 9000 порту, перенаправит на 9090

127.0.0.1:9090/

Далее авторизуетесь

login: minioadmin

password: minoadmin

Создаете bucket с названием uchetkzbucket. access key добавлять не нужно!

Врубаете локально сервер

uvicorn api:app 

по адресу

0.0.0.0:8000/docs

должны увидеть upload_file

Загружаете файл и проверяете в s3 uchetkzbucket загрузилось ли. 

Коменнтарии по реализации в service.py
