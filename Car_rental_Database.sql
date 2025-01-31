CREATE SEQUENCE IF NOT EXISTS public.admins_id_seq
    INCREMENT 1
    START WITH 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
	
CREATE SEQUENCE IF NOT EXISTS public.cars_id_seq
   INCREMENT 1
    START WITH 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
	
CREATE SEQUENCE IF NOT EXISTS public.users_id_seq
    INCREMENT 1
    START WITH 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
	
CREATE SEQUENCE IF NOT EXISTS public.bookings_id_seq
    INCREMENT 1
    START WITH 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
	
CREATE SEQUENCE IF NOT EXISTS public.sos_alerts_id_seq
    INCREMENT 1
    START WITH 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
	

	

	
	


CREATE TABLE IF NOT EXISTS public.admins
(
    id integer NOT NULL DEFAULT nextval('admins_id_seq'::regclass),
    username character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT admins_pkey PRIMARY KEY (id),
    CONSTRAINT admins_username_key UNIQUE (username)
);


	

CREATE TABLE IF NOT EXISTS public.cars
(
    id integer NOT NULL DEFAULT nextval('cars_id_seq'::regclass),
    make character varying(255) COLLATE pg_catalog."default" NOT NULL,
    model character varying(255) COLLATE pg_catalog."default" NOT NULL,
    year integer NOT NULL,
    mileage integer NOT NULL,
    available boolean DEFAULT true,
    min_rent_period integer NOT NULL,
    max_rent_period integer NOT NULL,
    rental_charge_per_hour numeric(10,2) NOT NULL DEFAULT 0,
    tax_rate numeric(5,2) NOT NULL DEFAULT 0,
    CONSTRAINT cars_pkey PRIMARY KEY (id)
);



	

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    role character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT 'user'::character varying,
    email character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT uni UNIQUE (email),
    CONSTRAINT users_username_key UNIQUE (username)
);



	
CREATE TABLE IF NOT EXISTS public.bookings
(
    id integer NOT NULL DEFAULT nextval('bookings_id_seq'::regclass),
    user_id integer NOT NULL,
    car_id integer NOT NULL,
    rental_start timestamp without time zone NOT NULL,
    rental_end timestamp without time zone NOT NULL,
    status character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT 'awaiting approval'::character varying,
    total_fee numeric(10,2) NOT NULL,
    comments text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    CONSTRAINT bookings_pkey PRIMARY KEY (id),
    CONSTRAINT bookings_car_id_fkey FOREIGN KEY (car_id)
        REFERENCES public.cars (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);




CREATE TABLE IF NOT EXISTS public.sos_alerts
(
    id integer NOT NULL DEFAULT nextval('sos_alerts_id_seq'::regclass),
    user_id integer,
    message text COLLATE pg_catalog."default",
    sent_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT sos_alerts_pkey PRIMARY KEY (id),
    CONSTRAINT sos_alerts_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);



	