## Посилання
[digitalocean docs](https://docs.digitalocean.com/products/networking/dns/getting-started/dns-registrars/)

[godaddy](https://godaddy.com/)


%ukkjK5$J7&59JC

## Оновлюємо списки пакетів та встановлюємо всі доступні оновлення.
``` commandline
sudo apt update
```
``` commandline
sudo apt upgrade
```

## Перезапускаємо сервер після оновлень.
``` commandline
sudo shutdown -r now
```

## Встановлюємо веб-сервер Nginx та перевіряємо його статус.
``` commandline
sudo apt install -y nginx
```
``` commandline
sudo systemctl status nginx
```

## Перевіряємо стан фаєрволу UFW, дозволяємо SSH, HTTP і HTTPS, перезавантажуємо правила.
``` commandline
sudo ufw status
```
``` commandline
sudo ufw allow ssh
```
``` commandline
sudo ufw allow 'Nginx Full'
```
``` commandline
sudo ufw reload
```
``` commandline
sudo ufw status
```
``` commandline
sudo ufw enable
```
``` commandline
sudo ufw status
```

## Встановлюємо Certbot і автоматично налаштовуємо HTTPS для домену.
``` commandline
sudo apt install -y certbot python3-certbot-nginx
```
``` commandline
sudo certbot --nginx -d the-best-fastapi-project.online  --agree-tos --email your-email@example.com --non-interactive --redirect
```

## Перевіряємо, чи коректно працює авто-оновлення.
``` commandline
sudo certbot renew --dry-run
```

## Вимикаємо дефолтний сайт і створюємо власний конфіг nginx.
``` commandline
sudo unlink /etc/nginx/sites-enabled/default
```
``` commandline
cd /etc/nginx/sites-available
```
``` commandline
sudo nano app.conf
```
-- файл (змінити на вміст DEPLOY_VPS -> nginx.conf) - save and exit

## Активуємо сайт та перезапускаємо Nginx. Створюємо симлінк, тестуємо конфігурацію та перезапускаємо сервіс.
``` commandline
sudo ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/app.conf
```
``` commandline
sudo nginx -t
```
``` commandline
sudo systemctl restart nginx
```

## Додаємо ключі Docker, репозиторій, встановлюємо Docker Engine, CLI, compose-plugin і перевіряємо роботу.
``` commandline
cd
```
``` commandline
sudo apt update
```
``` commandline
sudo apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
```
``` commandline
sudo mkdir -p /etc/apt/keyrings
```

### встановлення докеру з GPG ключами

| GPG-ключ (GNU Privacy Guard key) — це криптографічний ключ, який використовується для підпису та перевірки цілісності даних, 
  у нашому випадку — APT-пакетів, що встановлюються через репозиторії Linux.

``` commandline
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
``` commandline
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
``` commandline
sudo apt update
```
``` commandline
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
``` commandline
sudo systemctl status docker.service
```
``` commandline
docker -v
```
``` commandline
docker compose version
```

## Підготовка проєкту до запуску Docker-контейнерів. Створюємо директорію, файл docker-compose і запускаємо його.
``` commandline
sudo mkdir app
```
``` commandline
cd app
```
``` commandline
sudo nano docker-compose.yml
```
-- добавляємо вміст DEPLOY_VPS/docker-compose.yaml
``` commandline
sudo nano .env
```
-- добавляємо вміст .env (без дебагу)
``` commandline
sudo docker compose up
```
``` commandline
sudo docker compose up  -d
```
``` commandline
docker logs -f backend1
```

## Видалення сертифікатів і вимкнення Nginx
``` commandline
sudo docker compose down
```
``` commandline
sudo systemctl stop nginx
```
``` commandline
sudo systemctl disable nginx
```
``` commandline
sudo rm /etc/nginx/sites-enabled/app.conf
```
``` commandline
sudo rm /etc/nginx/sites-available/app.conf
```
``` commandline
sudo nginx -t
```
``` commandline
sudo systemctl restart nginx
```

``` commandline
sudo certbot certificates
```
``` commandline
sudo certbot delete --cert-name the-best-fastapi-project.online
```