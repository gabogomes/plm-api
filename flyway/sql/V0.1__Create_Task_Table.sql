create table if not exists task
(
    id integer not null generated always as identity,
    name text not null,
    status text not null,
    type text not null,
    user_id text not null,
    correspondence_email_address text not null,
    created_by text not null,
    created_on timestamp not null,
    modified_by text,
    modified_on timestamp,

    constraint task_pkey primary key(id)
);
