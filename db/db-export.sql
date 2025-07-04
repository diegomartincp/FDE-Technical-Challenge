--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5

-- Started on 2025-07-04 03:43:18

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 65547)
-- Name: call_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.call_logs (
    call_id integer NOT NULL,
    call_timestamp timestamp without time zone DEFAULT now() NOT NULL,
    carrier_id integer,
    load_id integer,
    sale_closed boolean NOT NULL,
    sentiment character varying(20) NOT NULL,
    notes text,
    duration integer,
    agent_name character varying(100),
    negotiation_rounds integer,
    CONSTRAINT chk_sentiment CHECK (((sentiment)::text = ANY ((ARRAY['sentiment-positive'::character varying, 'sentiment-neutral'::character varying, 'sentiment-negative'::character varying])::text[])))
);


ALTER TABLE public.call_logs OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 65546)
-- Name: call_logs_call_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.call_logs_call_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.call_logs_call_id_seq OWNER TO postgres;

--
-- TOC entry 3377 (class 0 OID 0)
-- Dependencies: 219
-- Name: call_logs_call_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.call_logs_call_id_seq OWNED BY public.call_logs.call_id;


--
-- TOC entry 218 (class 1259 OID 65538)
-- Name: loads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.loads (
    load_id integer NOT NULL,
    origin character varying(100) NOT NULL,
    destination character varying(100) NOT NULL,
    pickup_datetime timestamp without time zone NOT NULL,
    delivery_datetime timestamp without time zone NOT NULL,
    equipment_type character varying(50),
    loadboard_rate numeric(10,2),
    notes text,
    weight numeric(10,2),
    commodity_type character varying(100),
    num_of_pieces integer,
    miles integer,
    dimensions character varying(100)
);


ALTER TABLE public.loads OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 65537)
-- Name: loads_load_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.loads_load_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.loads_load_id_seq OWNER TO postgres;

--
-- TOC entry 3378 (class 0 OID 0)
-- Dependencies: 217
-- Name: loads_load_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.loads_load_id_seq OWNED BY public.loads.load_id;


--
-- TOC entry 3216 (class 2604 OID 65550)
-- Name: call_logs call_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_logs ALTER COLUMN call_id SET DEFAULT nextval('public.call_logs_call_id_seq'::regclass);


--
-- TOC entry 3215 (class 2604 OID 65541)
-- Name: loads load_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loads ALTER COLUMN load_id SET DEFAULT nextval('public.loads_load_id_seq'::regclass);


--
-- TOC entry 3371 (class 0 OID 65547)
-- Dependencies: 220
-- Data for Name: call_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.call_logs (call_id, call_timestamp, carrier_id, load_id, sale_closed, sentiment, notes, duration, agent_name, negotiation_rounds) FROM stdin;
1	2025-07-03 17:07:44.528282	123456	1	t	sentiment-neutral	The transcript is empty, so there is no information to summarize. Please provide details or content from the call for a summary.	0	Alex	2
\.


--
-- TOC entry 3369 (class 0 OID 65538)
-- Dependencies: 218
-- Data for Name: loads; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.loads (load_id, origin, destination, pickup_datetime, delivery_datetime, equipment_type, loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions) FROM stdin;
1	Atlanta, GA	Dallas, TX	2025-07-10 08:00:00	2025-07-12 17:00:00	Dry Van	2000.00	No special requirements	20000.00	Electronics	22	800	48x102x110
2	Chicago, IL	Miami, FL	2025-07-15 09:00:00	2025-07-17 18:00:00	Reefer	3500.00	Temperature controlled	18000.00	Produce	18	1300	53x102x110
3	Los Angeles, CA	Denver, CO	2025-07-11 07:00:00	2025-07-12 20:00:00	Flatbed	2500.00	Straps required	22000.00	Steel	10	1000	40x96x100
4	Houston, TX	Phoenix, AZ	2025-07-13 10:00:00	2025-07-14 15:00:00	Dry Van	1800.00	No pallet jack needed	15000.00	Clothing	30	1170	48x102x110
5	Newark, NJ	Boston, MA	2025-07-16 06:00:00	2025-07-16 20:00:00	Box Truck	1200.00	Liftgate required	7000.00	Books	12	225	24x96x90
\.


--
-- TOC entry 3379 (class 0 OID 0)
-- Dependencies: 219
-- Name: call_logs_call_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.call_logs_call_id_seq', 1, true);


--
-- TOC entry 3380 (class 0 OID 0)
-- Dependencies: 217
-- Name: loads_load_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.loads_load_id_seq', 5, true);


--
-- TOC entry 3222 (class 2606 OID 65556)
-- Name: call_logs call_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_logs
    ADD CONSTRAINT call_logs_pkey PRIMARY KEY (call_id);


--
-- TOC entry 3220 (class 2606 OID 65545)
-- Name: loads loads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loads
    ADD CONSTRAINT loads_pkey PRIMARY KEY (load_id);


-- Completed on 2025-07-04 03:43:18

--
-- PostgreSQL database dump complete
--

