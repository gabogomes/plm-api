create table if not exists personal_note
(
    id integer not null generated always as identity,
    task_id int not null,
    name text not null,
    type text not null,
    note text not null,
    user_id text not null,
    correspondence_email_address text not null,
    created_by text not null,
    created_on timestamp not null,
    modified_by text,
    modified_on timestamp,

    constraint personal_note_pkey primary key(id),
    constraint personal_note_task_id_fkey foreign key (task_id) references task(id)
);