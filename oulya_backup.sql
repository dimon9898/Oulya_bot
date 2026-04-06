--
-- PostgreSQL database dump
--

\restrict 0gcxdJyQfOONfrilSlf3fcf1VRzU7EcCAuaytaYjt7koVVu4AILR4q2xdnvWdLl

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 18.1 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: contests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contests (
    id integer NOT NULL,
    enabled boolean NOT NULL,
    description character varying(512)
);


ALTER TABLE public.contests OWNER TO postgres;

--
-- Name: contests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contests_id_seq OWNER TO postgres;

--
-- Name: contests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contests_id_seq OWNED BY public.contests.id;


--
-- Name: course_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.course_items (
    id integer NOT NULL,
    name character varying(50),
    description character varying(768),
    category_id integer NOT NULL,
    is_active boolean NOT NULL,
    url character varying(512) NOT NULL,
    template_url character varying(512) NOT NULL
);


ALTER TABLE public.course_items OWNER TO postgres;

--
-- Name: course_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.course_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_items_id_seq OWNER TO postgres;

--
-- Name: course_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.course_items_id_seq OWNED BY public.course_items.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    description character varying(1024) NOT NULL,
    price numeric(10,2) NOT NULL,
    is_active boolean NOT NULL,
    photo_type character varying(3) NOT NULL,
    photo_url character varying(1024) NOT NULL
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchases (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    price numeric(10,2) NOT NULL,
    payment_id character varying(128),
    payment_status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    paid_at timestamp with time zone
);


ALTER TABLE public.purchases OWNER TO postgres;

--
-- Name: purchases_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.purchases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchases_id_seq OWNER TO postgres;

--
-- Name: purchases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.purchases_id_seq OWNED BY public.purchases.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    user_id bigint,
    create_at timestamp without time zone NOT NULL,
    came_from character varying(50),
    is_active boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: contests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contests ALTER COLUMN id SET DEFAULT nextval('public.contests_id_seq'::regclass);


--
-- Name: course_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_items ALTER COLUMN id SET DEFAULT nextval('public.course_items_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: purchases id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases ALTER COLUMN id SET DEFAULT nextval('public.purchases_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
3d82278b297f
\.


--
-- Data for Name: contests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contests (id, enabled, description) FROM stdin;
1	f	Крутой конкурс
\.


--
-- Data for Name: course_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.course_items (id, name, description, category_id, is_active, url, template_url) FROM stdin;
37	null	null	4	t	f9LHodD0cOIsh9xE2NAO-RE7coMvDwsVMdFCcMb1NgI8z6OaHMJL5VRx1faPYOl6j4Lm-csmvV-UgN7RQTQa	null
38	null	null	4	t	f9LHodD0cOLN4Nhr3e0gh9XaV9GnYRlfSvZ9MnD2XjbS7P7axRKIUSxMH9uZZVt1sgFWh1BaHJvk6dV7yy17	null
1	Соединение синельной проволоки	Возьмите два отрезка проволоки, которые необходимо соединить. Плотно приложите их кончики друг к другу и аккуратно перекрутите, чтобы они надежно сцепились. Такой способ соединения обеспечивает прочность и устойчивость, создавая надежную основу для дальнейшего моделирования и декоративной работы.	1	t	f9LHodD0cOLVmvBELqrZqh0qjb6j3AlOFS4plj6xl39DPP3EiknhR5OAks7km6-CGYMgq8g3IvBiRZDlrPee	null
8	Создание тонких деталей	Если необходимо выполнить изящные и деликатные элементы, аккуратно обрежьте ворсинки на синельной проволоке почти до самой основы. В результате получится гладкая и тонкая проволочка, из которой удобно формировать миниатюрные детали. Такой приём особенно подходит для создания лапок у насекомых, усиков или тычинок у цветков.	1	t	f9LHodD0cOLhsy17N3X2onsbnTy26kFs3M9tW9RRtxVE30XL0sBGXUeAWo00MyNtzzKf3L89Y49zD7JH5tCk	null
9	Добавление объёма	Чтобы придать изделию выразительность и глубину, можно слегка затонировать отдельные участки детали. Для этого аккуратно нанесите сухую пастель на выбранные места, создавая эффект объёма и мягких теней. Такой приём сделает работу более реалистичной, добавит ей завершённости и художественного изящества.	1	t	f9LHodD0cOI1V40a9JIVvBp5pFmjamILnTfkkzbiSbKG5bWy5W6MWdqI4oAQWBgE0xPVZ85rQqc1tWlcHI1H	null
10	Основной принцип создания лепестков и листиков	Чтобы сформировать лепесток или листик, возьмите две синельные проволоки и скрутите их вместе посередине. Зафиксируйте перекрут на нужной высоте, после чего аккуратно разогните концы, придавая им форму лепестка или листа. Такой способ позволяет легко создавать основу для цветочных композиций.	1	t	f9LHodD0cOJIhvKwwHKFA1mrhCZ0qgEkiQxa1x2T2Rz8rWTe9clO314dC0Q7DHt8ZT4xs3xi3MxWL_6VmdP5	null
11	Создание длинных листьев	Для формирования длинного листа используйте тот же принцип, что и при изготовлении лепестков. Соедините две синельные проволоки и зафиксируйте их у основания. Затем аккуратно выгибайте проволоку, придавая ей вытянутую форму листа. Такой способ позволяет создавать изящные и реалистичные элементы для цветочных композиций.	1	t	f9LHodD0cOIXpBiXdZ_BmxP1IoAr81r-YCNbO__Nyd-PNviBKpJLFQBSCchaRiDJMQTwvA5ahJAvlMMEM_og	null
22	Дракон из синельной проволоки	Тонировка	2	t	f9LHodD0cOLwWfgq-Aa_SQKtv1tDQGqn4wWTzLeV9EQQVnMZuusjPpcxcIDRDNyQP8Vu9lDALwlwwEUeJe7f	null
24	null	null	3	t	f9LHodD0cOLj8MfsXEjY8ba3QdxrPRNbLE4U44-xR9qJdjoxD6sashBDncXiPMFA3-UwKXCWyxUgSmgnE3LK	null
25	null	null	3	t	f9LHodD0cOLu0RDP5OZDojHu92nMIk9rcErdyf-kM-mONkcbBZLTKHMma-BRelFT_qxopUMJYRFbzRRPp0h9	null
26	null	null	3	t	f9LHodD0cOLPOTXOBuwI8FfVmglMEgzUpM5xGdOsELGNwWW5EsEauVkaFKexLjrFlI-s2HyOu9tYOnNpVR4x	null
27	null	null	3	t	f9LHodD0cOKANuRSxPUIdvEigeYm5nK25Iq3nKYpJZjhlmS3-bS07Vsl0rXKeT_nBNVp5BJ7Szev0QXQQZjT	null
28	null	null	3	t	f9LHodD0cOI9rD27Af05ERNQjmKbhkCu15rkbRQmKHIbjkS2j9Bu1AObV74XOC7tWpUJjAINmqL8q3NJfwT3	null
29	null	null	3	t	f9LHodD0cOJRC5zfHdwx4LDWVbTJQyRaIIuHVJknF_bM8lRPt30MKo9ozNOvDmi5pJNpBspYRbTMa4-_UOr8	null
30	null	null	3	t	f9LHodD0cOIydylFlI02zC944yRuTY2HhJ3-kDeMN96QQd5o4LFTU1YfcXf-RKkSHt-v7jXBGP5Kw5g8NOqo	null
31	null	null	3	t	f9LHodD0cOKeCpBG9yKGB7RKla-DisLrCZ2uDvJzqYtzu8K7gbtqn_aPLA8AAe1Ax_B_Hgo47U3uqaSXhPj-	null
32	null	null	3	t	f9LHodD0cOJegHYSeQMXWh-nR2jD9BoHs4TvTSPSSfKXl_luILooYT0fiZzU1LVU2nsQdV4rkHfIh9AsLzah	null
33	null	null	3	t	f9LHodD0cOL5LJCFrCjk_hq7UdlPOyy4w6EghU6k7CPOaL4H9ihB3jBoBdgQAGHdMT0Ihk-LlRjGrI2cWa6e	null
34	null	null	3	t	f9LHodD0cOKOMSmXVrKA7nZvXJsFxL__hkWDzh6PpJR06x7zw2JIvktCZ0tztQ56geVfaRQFDFsd0u4Ti16d	null
35	null	null	3	t	f9LHodD0cOLIQYeU4KdLKckg0F35Ig_9jzPazVc4o0an3dutZ35bHAfK2gUTivKoyz3RjqnyAD3SJWZrDdD4	null
36	null	null	3	t	f9LHodD0cOJi6ZZTHbgwh1AyyyAI92J4mQsc0fwt4iUMiggq6HYH28x7MYv8cKDHdbK7o9HPqq6oeliRMcbe	null
39	null	null	4	t	f9LHodD0cOJHQphlbsTEl9Ql1Nv6HjvVy4_y7NtCBTExHO8nqKI3mlvO22jHF27zJe86dSMbYK5fMR6wfiA8	eQo/8DnYaBjZv2IZ+WuwTmAGmgWXS+fipanhxYAihQtsDW8Pa3zRn6qro1ehZeQNL+3lEUIo4OLtxG8XNUuhW15HjwYRJ1Et1Igs2PjZxGI=
40	null	null	4	t	f9LHodD0cOKUL9z8T985YNPvcrTn-GkE5_nlX61ObwKK7yHvpQ6-UaUOACMtBzb6juzrhpCDKV60x3xKjLGF	null
41	null	null	4	t	f9LHodD0cOJMgqiQ4q_x2xoBZ4TbXcdl1ptERtiiP8boUuaC6ltMkpJmU36eZ1GBdzNCQbuiwoTS8ucgQGQ7	bTzQuslttDKvebqIkBR7uyyR7crsI3TQJt0YU6ddJVN5Mx5Y5YZEIP2IpJnZe7t2myPvZrlJB96GLVjDmVvUq9DYyVPiSrZYaGANQcRTnNw=
42	null	null	4	t	f9LHodD0cOJit-qkzZlDU6G8_dJYNlM5INSVaxBqaKTUcDVievR4mAs4PMoA_TQm66s2XVNuorv3Dk3wq4Vi	null
43	null	null	4	t	f9LHodD0cOKps2Mo1N0LEuS9y3b-2mtr0Z99XwWodQoBeVlWkpu4eO4qmaf6teeYRobeL2yDifvRJJRx2o-M	yEdnA/feN/SUBAy/pnz0OCncbI9+OEsSpZvu8qzcSZPhp6tq0seFSk+tjH1Wo83uQlTYSQFyIkiChkLGqrVTP3NMihgb+/8YX5qkxLp6Mxc=
44	null	null	4	t	f9LHodD0cOJBVfDJahhTJwKadwxZpZUurDXXknRM9pEa_7QkbdbUUrKFm5D1-ZQCgSjms-3OugpeAY02srzq	2zf9ep5S91r2urXEupQovzzxiT2P3k/pYV0Ij3/BrStD5I53tVPPYhlV/OeYqYUKKbAsg1VDOPXFI9u94/khluVjyUtBDgZ7jY9ZmDzq0g4=
45	null	null	4	t	f9LHodD0cOKOcX6VoHdL0RCgb62Pe_J0XZ0aj9Dh6w5aZzgnHHhWute4wmdihCYQpJDy-x_nMKAC__Vln7h1	Zt2Eyw7cYeurUzM3LSqWDGF/vnX67HmRRBycOuQ9unVi6ErKNayyiGcJvQrhFdnJXo/rQsAe9yUrJGNpmj0dcXHZOxY5E7WjLF1nne3LVFw=
14	Создание мелких цветочков (например, ромашек)	Для изготовления небольших цветочков используйте простой и удобный приём. Намотайте синельную проволоку вокруг карандаша или ручки столько раз, сколько лепестков хотите получить. Каждая намотка образует один лепесток, поэтому их количество будет равно числу витков. Сняв заготовку с основы, аккуратно расправьте лепестки — у вас получится изящная ромашка или другой миниатюрный цветочек.	1	t	f9LHodD0cOJsCPaK3EKZdXopohm1NQUGXNxcZo-3BectLELCDVX03zn6XXf10t-sE3NqrQpRq1Lec5mevA1W	null
15	Создание круглых лепестков	Чтобы получить лепесток более округлой формы, принцип слегка отличается от стандартного. Отмерьте участок синельной проволоки длиной около 5–6 см и зафиксируйте его. Затем аккуратно согните проволоку, возвращаясь к исходной точке, формируя плавный округлый контур. Такой способ позволяет создавать нежные лепестки, идеально подходящие для тюльпанов и других цветов с мягкой формой.	1	t	f9LHodD0cOKQ9vaLyGg6pE2DEBRC_52RPoVwXYiFnkFHogsUrWbrcxiK1WkDGGdNUEUdK1rL8gLUZByE4Yb0	null
16	Создание плоских фигур из проволоки	Чтобы изготовить плоскую фигурку, сначала сформируйте каркас нужной формы — это может быть контур буквы, геометрической фигуры или декоративного элемента. Затем начинайте аккуратно обматывать каркас синельной проволокой, образуя небольшие «петли» вокруг основы. Благодаря такому приёму фигура получится прочной и будет одинаково аккуратной с обеих сторон. Этот способ особенно удобен для создания крыльев, листьев и других плоских декоративных деталей.	1	t	f9LHodD0cOITbGg24q9GPSJyyD5eDHDC-l4LOlFFEBPvgqqyEuB9J8nJd2N7HBaI2nNEXsCoZfXE6fGRJ_Eg	null
17	Создание больших и объёмных фигур	Чтобы сделать крупную или объёмную фигуру, сначала сформируйте прочный каркас из проволоки, придав ему желаемую форму. Затем начинайте равномерно обматывать каркас синельной проволокой, следя за тем, чтобы витки проходили сверху и плотно фиксировали конструкцию. Если отрезок проволоки закончился, добавьте новый: аккуратно закрепите его на каркасе, чтобы сохранить прочность и целостность изделия. Такой способ позволяет создавать устойчивые и выразительные объёмные формы.	1	t	f9LHodD0cOLrivkARY5StB30pE3xcJVHL2HVs6m_M3fmL5UozoX0K4BFiQUReyEqdkizqlFxb2IWl2R7ct64	null
2	Создание пружинки\n	Чтобы сделать пружинку, возьмите синельную проволоку и аккуратно намотайте её на карандаш или ручку. Старайтесь располагать витки плотно и равномерно — так пружинка получится аккуратной и упругой. После намотки снимите её с основы, и у вас будет готовый элемент для украшения или дальнейших поделок.	1	t	f9LHodD0cOLK3GXEq7jX0VvwdIdIZZXUmUPPPkMOYk_r4uG5z7Rcru9WYcV_5lgYB6miS1I663OLh6Dxu8jy	null
3	Формирование круга\n	Чтобы создать круг, начните аккуратно сворачивать синельную проволоку по спирали. Постепенно придавайте ей нужный размер и форму, следя за тем, чтобы витки ложились ровно. Кончик проволоки можно спрятать внутрь спирали или зафиксировать каплей клея — это сделает изделие более аккуратным и предотвратит его распускание.	1	t	f9LHodD0cOKSmeY6iZmgAdRXS7L_VCrnVaKo2csluHAFXB3tcyZ857Gh4W5ZIL9Eb-mAFuntXIIFhQUPtSXF	null
6	Создание шарика\n	Для изготовления шарика зажмите один конец синельной проволоки плоскогубцами или просто крепко удерживайте его пальцами. Свободный конец начинайте наматывать в разных направлениях, постепенно придавая заготовке объём и округлую форму. Такой способ позволяет получить аккуратный, плотный и равномерный шарик, который можно использовать как самостоятельный элемент или часть поделки.	1	t	f9LHodD0cOIUaPRbRW24_-0eI3DsxVzV99vi0C539OzPU0i-mGp6EYx6FW7lnjjMo8D2pcrMI-4fDiK6Sv4m	null
7	Формирование острых углов\n	Чтобы получить чёткие и выразительные острые углы, аккуратно подрежьте ворсинки на синельной проволоке в нужных местах. Благодаря этому кончики станут более резкими и будут лучше держать форму. Такой приём особенно удобен при создании деталей с гранями, где требуется точность и аккуратность.	1	t	f9LHodD0cOJcJ_CVlN-9EmFLRpa36TE-tA5lpN9ltlZPIyPXR_9K0t323BCfUGe1Hb1mJKE3xCWFhqUrYP_L	null
19	Дракон из синельной проволоки	Лапы	2	t	f9LHodD0cOL2xb19N3GQ7Rr7tYpKhYSPL6MK1Z512UEmR4QXMF7qaAbnK7vFvbrZo3ut2Dhdnyu1VgRIoRCh	null
21	Дракон из синельной проволоки	Детали	2	t	f9LHodD0cOKxtyB_xzza1jq13hMADeYafWyBGg7b27Vg5oYR9KuWSIYtk6X8I2eC9RC4pXSpyfJXVrZ3eJTQ	null
23	null	null	3	t	f9LHodD0cOJoSIXq0uK-ssja38_xIS5X3OIoVecLQ6oE9Ibobeu3j6fA2fECkSrcvW5chPTfMdPU85pnuhGP	null
20	Дракон из синельной проволоки	Хвост и крылья	2	t	f9LHodD0cOK9NXBW9Q5KK9VymUWQqqRGWdV9ReTvwfyz1fP0DUg0HFjfDQIEQQwV6tUISV0w9TjddXq3QolD	null
18	Дракон из синельной проволоки	Голова и тело	2	t	f9LHodD0cOLcFt94_RmsFDJ7PxF2WAkwyipAz50pBhyWt0zZnKIGgN7iHCnjiHHUOSU2ATTtreRJBL_ZOwHt	null
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.courses (id, title, description, price, is_active, photo_type, photo_url) FROM stdin;
4	Фетр: базовые основы и поделки	null	199.00	t	nul	www
2	Дракон из синельной проволоки	5 шагов — и у тебя свой дракон. смотри видео, повторяй и играй. начни сейчас!	299.00	t	jpg	MyQfnF/RIiCPm+kciwlIqSqjLtcjkMUYkdZcyNCdiZKJyqbHBgOP/fkX7MkhivJf3TjdB5eXiK4xjOc9FNFqPnzeS4x2Mxns/5Syv7CeF7c=
3	🎨 Мини-курс “Мягкий пластилин: творчество без гра	Добро пожаловать в мир мягкого пластилина — тёплый, уютный и удивительно простой способ раскрыть в себе и в ребёнке творческий поток 💛  📦 Внутри  ждёт:  базовый модуль — как правильно работать с мягким пластилином: секреты, лайфхаки, хранение;  4 пошаговых мастер-класса: ✨ картина из пластилина, 🧁 яркое пирожное, 🧲 милые магниты на холодильник, 🎀 и забавный обвес для декора.  Вы увидите, что лепка может быть не только полезной, но и невероятно расслабляющей. Каждый урок — короткий, понятный и вдохновляющий, даже если вы никогда раньше не лепили!  👩‍👧 Этот курс подойдёт:  мамам, которые хотят творить с детьми, педагогам и творческим наставникам, всем, кто ищет простое удовольствие своими руками.  💫 Готовы попробовать? Начните прямо сейчас — удовольствие гарантировано!	199.00	t	jpg	hwh+37cyOLL2uglqsWMetVmrWBCeY/s5qLJVQs9JLiQE/HZoYpul2UsdxYdvqCwfVkvVvmMzfLbBG4IVPEMgEsLLv2OOQatus7R5fme6D78=
1	Базовый курс по синельной проволоке	13 техник = бесконечное творчество!  Синельная проволока — это больше, чем просто детское хобби! Наш курс покажет вам, как из обычных пушистых палочек создавать удивительные поделки: от изящных цветов до объемных фигур.  Что внутри: ✅ 13 профессиональных видеоуроков ✅ Пошаговые текстовые инструкции к каждому видео ✅ Техники от базовых до продвинутых ✅ Секреты создания объема и детализации ✅ Готовые идеи для подарков и декора  Начните творить уже сегодня!	99.00	f	gif	f9LHodD0cOInrEo96BhCKvCE5b3NkOXeng4AGymT-LqnB_Z5cqobObXIh8VLpFOPNKbT2_UV30kUJp3XwbzU
\.


--
-- Data for Name: purchases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.purchases (id, user_id, course_id, price, payment_id, payment_status, created_at, updated_at, paid_at) FROM stdin;
18	7	2	299.00	31608448-000f-5001-9000-1f6ee3dae6d9	payment.succeeded	2026-04-02 13:35:04.306279+00	2026-04-02 13:35:57.983542+00	2026-04-02 13:35:57.978872+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, user_id, create_at, came_from, is_active) FROM stdin;
7	190522602	2026-04-01 11:42:46.303237	Ozon	t
\.


--
-- Name: contests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contests_id_seq', 1, true);


--
-- Name: course_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.course_items_id_seq', 45, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 4, true);


--
-- Name: purchases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.purchases_id_seq', 18, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: contests contests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contests
    ADD CONSTRAINT contests_pkey PRIMARY KEY (id);


--
-- Name: course_items course_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_items
    ADD CONSTRAINT course_items_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: course_items course_items_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_items
    ADD CONSTRAINT course_items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.courses(id);


--
-- Name: purchases purchases_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: purchases purchases_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict 0gcxdJyQfOONfrilSlf3fcf1VRzU7EcCAuaytaYjt7koVVu4AILR4q2xdnvWdLl

