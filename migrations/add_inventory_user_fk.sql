-- Migrasi database lama (PostgreSQL):
-- 1. Jalankan skrip ini jika tabel users dan inventories sudah ada.
-- 2. user_id dibuat nullable agar inventory lama tetap tersimpan.
-- 3. Buat user terlebih dahulu, lalu isi inventories.user_id untuk setiap baris lama.
-- 4. Setelah itu, jadikan kolom NOT NULL dengan ALTER TABLE di bawah.

alter table inventories
  add column if not exists user_id integer;

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'fk_inventories_user_id_users'
  ) then
    alter table inventories
      add constraint fk_inventories_user_id_users
      foreign key (user_id) references users (id) on delete restrict;
  end if;
end $$;

create index if not exists ix_inventories_user_id on inventories (user_id);

-- Setelah inventory lama diberi user_id yang valid, jalankan:
-- alter table inventories alter column user_id set not null;
