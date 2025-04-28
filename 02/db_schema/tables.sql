create table estate_agents
(
    name     varchar not null,
    address  varchar not null,
    login    varchar,
    password varchar,
    constraint estate_agents_pk
        primary key (name, address)
);

alter table estate_agents
    owner to vsisp26;

create table person
(
    first_name varchar not null,
    name       varchar not null,
    address    varchar not null,
    constraint person_pk
        primary key (first_name, name, address)
);

alter table person
    owner to vsisp26;

create table estates
(
    id            integer not null
        constraint estates_pk
            primary key,
    city          varchar,
    postal_code   integer,
    street        varchar,
    street_number integer,
    square_area   integer
);

alter table estates
    owner to vsisp26;

create table houses
(
    floors integer,
    price  integer,
    garden boolean,
    id     integer
        constraint housees_estates_id_fk
            references estates
);

alter table houses
    owner to vsisp26;

create table apartments
(
    id      integer not null
        constraint apartments_pk
            primary key
        constraint apartments_estates_id_fk
            references estates,
    floor   integer,
    rent    integer,
    rooms   integer,
    balcony boolean,
    kitchen boolean
);

alter table apartments
    owner to vsisp26;

create table contracts
(
    number integer not null
        constraint contracts_pk
            primary key,
    date   date,
    place  varchar
);

alter table contracts
    owner to vsisp26;

create table tenancy_contracts
(
    number           integer not null
        constraint tenancy_contracts_pk
            primary key
        constraint tenancy_contracts_contracts_number_fk
            references contracts,
    start_date       date,
    duration         integer,
    additional_costs integer
);

alter table tenancy_contracts
    owner to vsisp26;

create table purchase_contracts
(
    number              integer
        constraint purchase_contracts_contracts_number_fk
            references contracts,
    number_installments integer,
    interest_rate       double precision
);

alter table purchase_contracts
    owner to vsisp26;

create table manages
(
    name    varchar,
    address varchar,
    id      integer not null
        constraint manages_pk
            primary key
        constraint manages_estates_id_fk
            references estates,
    constraint manages_estate_agents_name_address_fk
        foreign key (name, address) references estate_agents
);

alter table manages
    owner to vsisp26;

create table sells
(
    id         integer
        constraint sells_estates_id_fk
            references estates,
    first_name varchar,
    name       varchar,
    address    varchar,
    number     integer
        constraint sells_contracts_number_fk
            references contracts,
    constraint sells_person_first_name_name_address_fk
        foreign key (first_name, name, address) references person
);

alter table sells
    owner to vsisp26;

create table rents
(
    number     integer not null
        constraint rents_pk
            primary key
        constraint rents_tenancy_contracts_number_fk
            references tenancy_contracts,
    id         integer
        constraint rents_apartments_id_fk
            references apartments,
    first_name varchar,
    name       varchar,
    address    varchar,
    constraint rents_person_first_name_name_address_fk
        foreign key (first_name, name, address) references person
);

alter table rents
    owner to vsisp26;

