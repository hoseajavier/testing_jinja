-- Jalankan sekali pada database yang sudah memiliki tabel inventories dan users.
create table inventory_users (
  inventory_id integer not null references inventories (id) on delete cascade,
  user_id integer not null references users (id) on delete cascade,
  primary key (inventory_id, user_id)
);

create index ix_inventory_users_user_id on inventory_users (user_id);
