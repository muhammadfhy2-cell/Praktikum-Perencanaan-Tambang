# Praktikum Perencanaan Tambang — Portal Django

Portal publik untuk informasi Praktikum Perencanaan Tambang. Pengunjung dapat melihat informasi dan mengunduh materi, sedangkan pengelolaan data dilakukan melalui Django Admin.

## Fitur
- Beranda, informasi praktikum, pengumuman, jadwal, kelompok, personel, materi, absensi, dan tata tertib.
- Struktur personel: **Penanggung Jawab Praktikum**, **Koordinator Asisten Dosen**, dan **Asisten Dosen**.
- Mentor kelompok dipilih dari data Asisten Dosen.
- Admin CRUD melalui `/admin/`.
- SQLite untuk lokal dan PostgreSQL untuk production.
- WhiteNoise untuk static files.
- Gunicorn untuk production.
- Environment variable melalui `.env`.
- `render.yaml` untuk deployment Render.

## Jalankan lokal Windows
```powershell
cd D:\praktikum_perencanaan_tambang
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Buka `http://127.0.0.1:8000/` dan `http://127.0.0.1:8000/admin/`.

## GitHub
```powershell
git init
git add .
git commit -m "Initial portal Praktikum Perencanaan Tambang"
git branch -M main
git remote add origin https://github.com/USERNAME/praktikum-perencanaan-tambang.git
git push -u origin main
```

## Deploy Render
1. Buat repository GitHub dan push project.
2. Di Render pilih **New Blueprint** atau gunakan `render.yaml` dari repository.
3. Pastikan service memakai `gunicorn core.wsgi:application`.
4. Pastikan environment production berisi `DEBUG=False` dan `SECRET_KEY` yang kuat.
5. `DATABASE_URL` harus menunjuk ke PostgreSQL Render.
6. `ALLOWED_HOSTS` dan `CSRF_TRUSTED_ORIGINS` harus memuat domain Render.
7. Setelah deploy, buka `/admin/` dan buat superuser melalui shell Render jika belum tersedia.

## Catatan file upload
Folder `media/` cocok untuk development. Untuk production dengan banyak materi/dataset, gunakan persistent disk atau object storage agar file tidak hilang ketika instance diganti/redeploy.

## Keamanan
- Jangan commit `.env`, database lokal, atau password ke GitHub.
- Gunakan `DEBUG=False` di production.
- Jangan menampilkan NIM, email, nomor telepon, atau detail absensi pribadi jika tidak diperlukan untuk publik.
