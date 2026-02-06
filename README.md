# 192.168.l.l Admin Giriş

Modem/yönlendiricinizin web yönetim sayfasına hızlıca ulaşmanızı sağlayan küçük, açık kaynaklı bir araç.

## Neden?
İnsanlar genellikle yanlışlıkla `192.168.l.l` (doğrusu `192.168.1.1`) yazıyor ve modem arayüzüne ulaşamıyorlar.

Bu komut dosyası:
- Varsayılan ağ geçidinizi algılar (mümkün olduğunda)
- Yaygın yönlendirici IP adreslerini kontrol eder
- HTTP/HTTPS'yi inceler ve çalışan bağlantıları yazdırır

## Kullanım
```bash
python3 gateway_finder.py


English:

# 192.168.l.l Modem Gateway Finder

Tiny open-source tool to quickly find your modem/router web admin page.

## Why?
People often type `192.168.l.l` by mistake (it's `192.168.1.1`) and can't reach the modem UI.
This script:
- detects your default gateway (when possible)
- checks common router IPs
- probes HTTP/HTTPS and prints working links

## Usage
```bash
python3 gateway_finder.py
