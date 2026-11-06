# VPS Üretim Sertleştirme ve Güvenlik Rehberi (VPS Hardening Playbook)

Ubuntu / Debian tabanlı bir VPS'e (Hetzner, DigitalOcean, AWS EC2, Linode vb.) ilk kez girildiğinde, uygulamayı ayağa kaldırmadan önce yapılması gereken güvenlik adımlarıdır.

---

## 1. Kullanıcı ve SSH Güvenliği

1. **Root ile Girişi Kapat ve Yeni Deploy Kullanıcısı Aç:**
   ```bash
   # Deploy kullanıcısı oluştur
   adduser deployer
   usermod -aG sudo deployer

   # SSH anahtarını deployer kullanıcısına kopyala
   mkdir -p /home/deployer/.ssh
   cp ~/.ssh/authorized_keys /home/deployer/.ssh/
   chown -R deployer:deployer /home/deployer/.ssh
   chmod 700 /home/deployer/.ssh
   chmod 600 /home/deployer/.ssh/authorized_keys
   ```

2. **`/etc/ssh/sshd_config` Düzenlemesi:**
   ```ini
   PermitRootLogin no
   PasswordAuthentication no
   PubkeyAuthentication yes
   X11Forwarding no
   ```
   *Yeniden başlat: `sudo systemctl restart sshd`*

---

## 2. UFW Güvenlik Duvarı (Firewall)

Sunucuda çalışan iç portların (Postgres 5432, Redis 6379, App 3000/8080) dış dünyaya kesinlikle kapatılması zorunludur:

```bash
# Varsayılan kurallar: Tüm gelenleri engelle, tüm gidenlere izin ver
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Yalnızca gerekli portları aç
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP (Let\'s Encrypt)'
sudo ufw allow 443/tcp comment 'HTTPS'

# Güvenlik duvarını aktifleştir
sudo ufw enable
sudo ufw status verbose
```

---

## 3. Fail2ban (Brute-Force Koruması)

SSH portuna sürekli şifre denemesi yapan bot IP'lerini otomatik banlamak için:

```bash
sudo apt update && sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 4. Let's Encrypt ve Otomatik SSL Yenileme (Certbot)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

*Certbot otomatik yenileme zamanlayıcısını denetle:*
```bash
sudo certbot renew --dry-run
```

---

## 5. Log Rotasyonu (Disk Dolmasını Önleme)

Docker veya systemd loglarının VPS diskini doldurup sunucuyu kilitlemesini engellemek için `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```
*Yeniden başlat: `sudo systemctl restart docker`*
