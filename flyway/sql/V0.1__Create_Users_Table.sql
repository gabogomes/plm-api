create table if not exists users
(
    id integer not null generated always as identity,
    name text not null,
    email_address text not null,
    password text not null,
    created_by text not null,
    created_on timestamp not null,
    modified_by text,
    modified_on timestamp,

    constraint user_pkey primary key(id)
);
