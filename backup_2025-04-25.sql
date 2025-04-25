--
-- PostgreSQL database dump
--

-- Dumped from database version 13.20 (Debian 13.20-1.pgdg120+1)
-- Dumped by pg_dump version 13.20 (Debian 13.20-1.pgdg120+1)

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
-- Name: ab_permission; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_permission (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.ab_permission OWNER TO airflow;

--
-- Name: ab_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_permission_id_seq OWNER TO airflow;

--
-- Name: ab_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_permission_id_seq OWNED BY public.ab_permission.id;


--
-- Name: ab_permission_view; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_permission_view (
    id integer NOT NULL,
    permission_id integer,
    view_menu_id integer
);


ALTER TABLE public.ab_permission_view OWNER TO airflow;

--
-- Name: ab_permission_view_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_permission_view_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_permission_view_id_seq OWNER TO airflow;

--
-- Name: ab_permission_view_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_permission_view_id_seq OWNED BY public.ab_permission_view.id;


--
-- Name: ab_permission_view_role; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_permission_view_role (
    id integer NOT NULL,
    permission_view_id integer,
    role_id integer
);


ALTER TABLE public.ab_permission_view_role OWNER TO airflow;

--
-- Name: ab_permission_view_role_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_permission_view_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_permission_view_role_id_seq OWNER TO airflow;

--
-- Name: ab_permission_view_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_permission_view_role_id_seq OWNED BY public.ab_permission_view_role.id;


--
-- Name: ab_register_user; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_register_user (
    id integer NOT NULL,
    first_name character varying(256) NOT NULL,
    last_name character varying(256) NOT NULL,
    username character varying(512) NOT NULL,
    password character varying(256),
    email character varying(512) NOT NULL,
    registration_date timestamp without time zone,
    registration_hash character varying(256)
);


ALTER TABLE public.ab_register_user OWNER TO airflow;

--
-- Name: ab_register_user_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_register_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_register_user_id_seq OWNER TO airflow;

--
-- Name: ab_register_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_register_user_id_seq OWNED BY public.ab_register_user.id;


--
-- Name: ab_role; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_role (
    id integer NOT NULL,
    name character varying(64) NOT NULL
);


ALTER TABLE public.ab_role OWNER TO airflow;

--
-- Name: ab_role_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_role_id_seq OWNER TO airflow;

--
-- Name: ab_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_role_id_seq OWNED BY public.ab_role.id;


--
-- Name: ab_user; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_user (
    id integer NOT NULL,
    first_name character varying(256) NOT NULL,
    last_name character varying(256) NOT NULL,
    username character varying(512) NOT NULL,
    password character varying(256),
    active boolean,
    email character varying(512) NOT NULL,
    last_login timestamp without time zone,
    login_count integer,
    fail_login_count integer,
    created_on timestamp without time zone,
    changed_on timestamp without time zone,
    created_by_fk integer,
    changed_by_fk integer
);


ALTER TABLE public.ab_user OWNER TO airflow;

--
-- Name: ab_user_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_user_id_seq OWNER TO airflow;

--
-- Name: ab_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_user_id_seq OWNED BY public.ab_user.id;


--
-- Name: ab_user_role; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_user_role (
    id integer NOT NULL,
    user_id integer,
    role_id integer
);


ALTER TABLE public.ab_user_role OWNER TO airflow;

--
-- Name: ab_user_role_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_user_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_user_role_id_seq OWNER TO airflow;

--
-- Name: ab_user_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_user_role_id_seq OWNED BY public.ab_user_role.id;


--
-- Name: ab_view_menu; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.ab_view_menu (
    id integer NOT NULL,
    name character varying(250) NOT NULL
);


ALTER TABLE public.ab_view_menu OWNER TO airflow;

--
-- Name: ab_view_menu_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.ab_view_menu_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ab_view_menu_id_seq OWNER TO airflow;

--
-- Name: ab_view_menu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.ab_view_menu_id_seq OWNED BY public.ab_view_menu.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO airflow;

--
-- Name: callback_request; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.callback_request (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    priority_weight integer NOT NULL,
    callback_data json NOT NULL,
    callback_type character varying(20) NOT NULL,
    processor_subdir character varying(2000)
);


ALTER TABLE public.callback_request OWNER TO airflow;

--
-- Name: callback_request_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.callback_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.callback_request_id_seq OWNER TO airflow;

--
-- Name: callback_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.callback_request_id_seq OWNED BY public.callback_request.id;


--
-- Name: connection; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.connection (
    id integer NOT NULL,
    conn_id character varying(250) NOT NULL,
    conn_type character varying(500) NOT NULL,
    description text,
    host character varying(500),
    schema character varying(500),
    login character varying(500),
    password character varying(5000),
    port integer,
    is_encrypted boolean,
    is_extra_encrypted boolean,
    extra text
);


ALTER TABLE public.connection OWNER TO airflow;

--
-- Name: connection_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.connection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.connection_id_seq OWNER TO airflow;

--
-- Name: connection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.connection_id_seq OWNED BY public.connection.id;


--
-- Name: dag; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag (
    dag_id character varying(250) NOT NULL,
    root_dag_id character varying(250),
    is_paused boolean,
    is_subdag boolean,
    is_active boolean,
    last_parsed_time timestamp with time zone,
    last_pickled timestamp with time zone,
    last_expired timestamp with time zone,
    scheduler_lock boolean,
    pickle_id integer,
    fileloc character varying(2000),
    processor_subdir character varying(2000),
    owners character varying(2000),
    description text,
    default_view character varying(25),
    schedule_interval text,
    timetable_description character varying(1000),
    max_active_tasks integer NOT NULL,
    max_active_runs integer,
    has_task_concurrency_limits boolean NOT NULL,
    has_import_errors boolean DEFAULT false,
    next_dagrun timestamp with time zone,
    next_dagrun_data_interval_start timestamp with time zone,
    next_dagrun_data_interval_end timestamp with time zone,
    next_dagrun_create_after timestamp with time zone
);


ALTER TABLE public.dag OWNER TO airflow;

--
-- Name: dag_code; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_code (
    fileloc_hash bigint NOT NULL,
    fileloc character varying(2000) NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    source_code text NOT NULL
);


ALTER TABLE public.dag_code OWNER TO airflow;

--
-- Name: dag_owner_attributes; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_owner_attributes (
    dag_id character varying(250) NOT NULL,
    owner character varying(500) NOT NULL,
    link character varying(500) NOT NULL
);


ALTER TABLE public.dag_owner_attributes OWNER TO airflow;

--
-- Name: dag_pickle; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_pickle (
    id integer NOT NULL,
    pickle bytea,
    created_dttm timestamp with time zone,
    pickle_hash bigint
);


ALTER TABLE public.dag_pickle OWNER TO airflow;

--
-- Name: dag_pickle_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.dag_pickle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dag_pickle_id_seq OWNER TO airflow;

--
-- Name: dag_pickle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.dag_pickle_id_seq OWNED BY public.dag_pickle.id;


--
-- Name: dag_run; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_run (
    id integer NOT NULL,
    dag_id character varying(250) NOT NULL,
    queued_at timestamp with time zone,
    execution_date timestamp with time zone NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    state character varying(50),
    run_id character varying(250) NOT NULL,
    creating_job_id integer,
    external_trigger boolean,
    run_type character varying(50) NOT NULL,
    conf bytea,
    data_interval_start timestamp with time zone,
    data_interval_end timestamp with time zone,
    last_scheduling_decision timestamp with time zone,
    dag_hash character varying(32),
    log_template_id integer,
    updated_at timestamp with time zone
);


ALTER TABLE public.dag_run OWNER TO airflow;

--
-- Name: dag_run_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.dag_run_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dag_run_id_seq OWNER TO airflow;

--
-- Name: dag_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.dag_run_id_seq OWNED BY public.dag_run.id;


--
-- Name: dag_run_note; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_run_note (
    user_id integer,
    dag_run_id integer NOT NULL,
    content character varying(1000),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.dag_run_note OWNER TO airflow;

--
-- Name: dag_schedule_dataset_reference; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_schedule_dataset_reference (
    dataset_id integer NOT NULL,
    dag_id character varying(250) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.dag_schedule_dataset_reference OWNER TO airflow;

--
-- Name: dag_tag; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_tag (
    name character varying(100) NOT NULL,
    dag_id character varying(250) NOT NULL
);


ALTER TABLE public.dag_tag OWNER TO airflow;

--
-- Name: dag_warning; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dag_warning (
    dag_id character varying(250) NOT NULL,
    warning_type character varying(50) NOT NULL,
    message text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE public.dag_warning OWNER TO airflow;

--
-- Name: dagrun_dataset_event; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dagrun_dataset_event (
    dag_run_id integer NOT NULL,
    event_id integer NOT NULL
);


ALTER TABLE public.dagrun_dataset_event OWNER TO airflow;

--
-- Name: dataset; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dataset (
    id integer NOT NULL,
    uri character varying(3000) NOT NULL,
    extra json NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    is_orphaned boolean DEFAULT false NOT NULL
);


ALTER TABLE public.dataset OWNER TO airflow;

--
-- Name: dataset_dag_run_queue; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dataset_dag_run_queue (
    dataset_id integer NOT NULL,
    target_dag_id character varying(250) NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.dataset_dag_run_queue OWNER TO airflow;

--
-- Name: dataset_event; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.dataset_event (
    id integer NOT NULL,
    dataset_id integer NOT NULL,
    extra json NOT NULL,
    source_task_id character varying(250),
    source_dag_id character varying(250),
    source_run_id character varying(250),
    source_map_index integer DEFAULT '-1'::integer,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE public.dataset_event OWNER TO airflow;

--
-- Name: dataset_event_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.dataset_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dataset_event_id_seq OWNER TO airflow;

--
-- Name: dataset_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.dataset_event_id_seq OWNED BY public.dataset_event.id;


--
-- Name: dataset_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.dataset_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dataset_id_seq OWNER TO airflow;

--
-- Name: dataset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.dataset_id_seq OWNED BY public.dataset.id;


--
-- Name: import_error; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.import_error (
    id integer NOT NULL,
    "timestamp" timestamp with time zone,
    filename character varying(1024),
    stacktrace text
);


ALTER TABLE public.import_error OWNER TO airflow;

--
-- Name: import_error_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.import_error_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.import_error_id_seq OWNER TO airflow;

--
-- Name: import_error_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.import_error_id_seq OWNED BY public.import_error.id;


--
-- Name: job; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.job (
    id integer NOT NULL,
    dag_id character varying(250),
    state character varying(20),
    job_type character varying(30),
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    latest_heartbeat timestamp with time zone,
    executor_class character varying(500),
    hostname character varying(500),
    unixname character varying(1000)
);


ALTER TABLE public.job OWNER TO airflow;

--
-- Name: job_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.job_id_seq OWNER TO airflow;

--
-- Name: job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.job_id_seq OWNED BY public.job.id;


--
-- Name: log; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.log (
    id integer NOT NULL,
    dttm timestamp with time zone,
    dag_id character varying(250),
    task_id character varying(250),
    map_index integer,
    event character varying(30),
    execution_date timestamp with time zone,
    owner character varying(500),
    extra text
);


ALTER TABLE public.log OWNER TO airflow;

--
-- Name: log_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.log_id_seq OWNER TO airflow;

--
-- Name: log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.log_id_seq OWNED BY public.log.id;


--
-- Name: log_template; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.log_template (
    id integer NOT NULL,
    filename text NOT NULL,
    elasticsearch_id text NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.log_template OWNER TO airflow;

--
-- Name: log_template_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.log_template_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.log_template_id_seq OWNER TO airflow;

--
-- Name: log_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.log_template_id_seq OWNED BY public.log_template.id;


--
-- Name: rendered_task_instance_fields; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.rendered_task_instance_fields (
    dag_id character varying(250) NOT NULL,
    task_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer DEFAULT '-1'::integer NOT NULL,
    rendered_fields json NOT NULL,
    k8s_pod_yaml json
);


ALTER TABLE public.rendered_task_instance_fields OWNER TO airflow;

--
-- Name: serialized_dag; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.serialized_dag (
    dag_id character varying(250) NOT NULL,
    fileloc character varying(2000) NOT NULL,
    fileloc_hash bigint NOT NULL,
    data json,
    data_compressed bytea,
    last_updated timestamp with time zone NOT NULL,
    dag_hash character varying(32) NOT NULL,
    processor_subdir character varying(2000)
);


ALTER TABLE public.serialized_dag OWNER TO airflow;

--
-- Name: session; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.session (
    id integer NOT NULL,
    session_id character varying(255),
    data bytea,
    expiry timestamp without time zone
);


ALTER TABLE public.session OWNER TO airflow;

--
-- Name: session_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_id_seq OWNER TO airflow;

--
-- Name: session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.session_id_seq OWNED BY public.session.id;


--
-- Name: sla_miss; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.sla_miss (
    task_id character varying(250) NOT NULL,
    dag_id character varying(250) NOT NULL,
    execution_date timestamp with time zone NOT NULL,
    email_sent boolean,
    "timestamp" timestamp with time zone,
    description text,
    notification_sent boolean
);


ALTER TABLE public.sla_miss OWNER TO airflow;

--
-- Name: slot_pool; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.slot_pool (
    id integer NOT NULL,
    pool character varying(256),
    slots integer,
    description text
);


ALTER TABLE public.slot_pool OWNER TO airflow;

--
-- Name: slot_pool_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.slot_pool_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.slot_pool_id_seq OWNER TO airflow;

--
-- Name: slot_pool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.slot_pool_id_seq OWNED BY public.slot_pool.id;


--
-- Name: task_fail; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_fail (
    id integer NOT NULL,
    task_id character varying(250) NOT NULL,
    dag_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer DEFAULT '-1'::integer NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    duration integer
);


ALTER TABLE public.task_fail OWNER TO airflow;

--
-- Name: task_fail_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.task_fail_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_fail_id_seq OWNER TO airflow;

--
-- Name: task_fail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.task_fail_id_seq OWNED BY public.task_fail.id;


--
-- Name: task_instance; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_instance (
    task_id character varying(250) NOT NULL,
    dag_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer DEFAULT '-1'::integer NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    duration double precision,
    state character varying(20),
    try_number integer,
    max_tries integer DEFAULT '-1'::integer,
    hostname character varying(1000),
    unixname character varying(1000),
    job_id integer,
    pool character varying(256) NOT NULL,
    pool_slots integer NOT NULL,
    queue character varying(256),
    priority_weight integer,
    operator character varying(1000),
    queued_dttm timestamp with time zone,
    queued_by_job_id integer,
    pid integer,
    executor_config bytea,
    updated_at timestamp with time zone,
    external_executor_id character varying(250),
    trigger_id integer,
    trigger_timeout timestamp without time zone,
    next_method character varying(1000),
    next_kwargs json
);


ALTER TABLE public.task_instance OWNER TO airflow;

--
-- Name: task_instance_note; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_instance_note (
    user_id integer,
    task_id character varying(250) NOT NULL,
    dag_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer NOT NULL,
    content character varying(1000),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.task_instance_note OWNER TO airflow;

--
-- Name: task_map; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_map (
    dag_id character varying(250) NOT NULL,
    task_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer NOT NULL,
    length integer NOT NULL,
    keys json,
    CONSTRAINT ck_task_map_task_map_length_not_negative CHECK ((length >= 0))
);


ALTER TABLE public.task_map OWNER TO airflow;

--
-- Name: task_outlet_dataset_reference; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_outlet_dataset_reference (
    dataset_id integer NOT NULL,
    dag_id character varying(250) NOT NULL,
    task_id character varying(250) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.task_outlet_dataset_reference OWNER TO airflow;

--
-- Name: task_reschedule; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.task_reschedule (
    id integer NOT NULL,
    task_id character varying(250) NOT NULL,
    dag_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    map_index integer DEFAULT '-1'::integer NOT NULL,
    try_number integer NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    duration integer NOT NULL,
    reschedule_date timestamp with time zone NOT NULL
);


ALTER TABLE public.task_reschedule OWNER TO airflow;

--
-- Name: task_reschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.task_reschedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_reschedule_id_seq OWNER TO airflow;

--
-- Name: task_reschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.task_reschedule_id_seq OWNED BY public.task_reschedule.id;


--
-- Name: trigger; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.trigger (
    id integer NOT NULL,
    classpath character varying(1000) NOT NULL,
    kwargs json NOT NULL,
    created_date timestamp with time zone NOT NULL,
    triggerer_id integer
);


ALTER TABLE public.trigger OWNER TO airflow;

--
-- Name: trigger_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.trigger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trigger_id_seq OWNER TO airflow;

--
-- Name: trigger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.trigger_id_seq OWNED BY public.trigger.id;


--
-- Name: variable; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.variable (
    id integer NOT NULL,
    key character varying(250),
    val text,
    description text,
    is_encrypted boolean
);


ALTER TABLE public.variable OWNER TO airflow;

--
-- Name: variable_id_seq; Type: SEQUENCE; Schema: public; Owner: airflow
--

CREATE SEQUENCE public.variable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.variable_id_seq OWNER TO airflow;

--
-- Name: variable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: airflow
--

ALTER SEQUENCE public.variable_id_seq OWNED BY public.variable.id;


--
-- Name: xcom; Type: TABLE; Schema: public; Owner: airflow
--

CREATE TABLE public.xcom (
    dag_run_id integer NOT NULL,
    task_id character varying(250) NOT NULL,
    map_index integer DEFAULT '-1'::integer NOT NULL,
    key character varying(512) NOT NULL,
    dag_id character varying(250) NOT NULL,
    run_id character varying(250) NOT NULL,
    value bytea,
    "timestamp" timestamp with time zone NOT NULL
);


ALTER TABLE public.xcom OWNER TO airflow;

--
-- Name: ab_permission id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission ALTER COLUMN id SET DEFAULT nextval('public.ab_permission_id_seq'::regclass);


--
-- Name: ab_permission_view id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view ALTER COLUMN id SET DEFAULT nextval('public.ab_permission_view_id_seq'::regclass);


--
-- Name: ab_permission_view_role id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view_role ALTER COLUMN id SET DEFAULT nextval('public.ab_permission_view_role_id_seq'::regclass);


--
-- Name: ab_register_user id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_register_user ALTER COLUMN id SET DEFAULT nextval('public.ab_register_user_id_seq'::regclass);


--
-- Name: ab_role id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_role ALTER COLUMN id SET DEFAULT nextval('public.ab_role_id_seq'::regclass);


--
-- Name: ab_user id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user ALTER COLUMN id SET DEFAULT nextval('public.ab_user_id_seq'::regclass);


--
-- Name: ab_user_role id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user_role ALTER COLUMN id SET DEFAULT nextval('public.ab_user_role_id_seq'::regclass);


--
-- Name: ab_view_menu id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_view_menu ALTER COLUMN id SET DEFAULT nextval('public.ab_view_menu_id_seq'::regclass);


--
-- Name: callback_request id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.callback_request ALTER COLUMN id SET DEFAULT nextval('public.callback_request_id_seq'::regclass);


--
-- Name: connection id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.connection ALTER COLUMN id SET DEFAULT nextval('public.connection_id_seq'::regclass);


--
-- Name: dag_pickle id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_pickle ALTER COLUMN id SET DEFAULT nextval('public.dag_pickle_id_seq'::regclass);


--
-- Name: dag_run id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run ALTER COLUMN id SET DEFAULT nextval('public.dag_run_id_seq'::regclass);


--
-- Name: dataset id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset ALTER COLUMN id SET DEFAULT nextval('public.dataset_id_seq'::regclass);


--
-- Name: dataset_event id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset_event ALTER COLUMN id SET DEFAULT nextval('public.dataset_event_id_seq'::regclass);


--
-- Name: import_error id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.import_error ALTER COLUMN id SET DEFAULT nextval('public.import_error_id_seq'::regclass);


--
-- Name: job id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.job ALTER COLUMN id SET DEFAULT nextval('public.job_id_seq'::regclass);


--
-- Name: log id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.log ALTER COLUMN id SET DEFAULT nextval('public.log_id_seq'::regclass);


--
-- Name: log_template id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.log_template ALTER COLUMN id SET DEFAULT nextval('public.log_template_id_seq'::regclass);


--
-- Name: session id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.session ALTER COLUMN id SET DEFAULT nextval('public.session_id_seq'::regclass);


--
-- Name: slot_pool id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.slot_pool ALTER COLUMN id SET DEFAULT nextval('public.slot_pool_id_seq'::regclass);


--
-- Name: task_fail id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_fail ALTER COLUMN id SET DEFAULT nextval('public.task_fail_id_seq'::regclass);


--
-- Name: task_reschedule id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_reschedule ALTER COLUMN id SET DEFAULT nextval('public.task_reschedule_id_seq'::regclass);


--
-- Name: trigger id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.trigger ALTER COLUMN id SET DEFAULT nextval('public.trigger_id_seq'::regclass);


--
-- Name: variable id; Type: DEFAULT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.variable ALTER COLUMN id SET DEFAULT nextval('public.variable_id_seq'::regclass);


--
-- Data for Name: ab_permission; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_permission (id, name) FROM stdin;
1	can_edit
2	can_read
3	can_create
4	can_delete
5	menu_access
6	muldelete
7	mulemailsent
8	mulemailsentfalse
9	mulnotificationsent
10	mulnotificationsentfalse
\.


--
-- Data for Name: ab_permission_view; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_permission_view (id, permission_id, view_menu_id) FROM stdin;
1	1	4
2	2	4
3	1	5
4	2	5
5	1	6
6	2	6
7	3	8
8	2	8
9	1	8
10	4	8
11	5	9
12	5	10
13	3	11
14	2	11
15	1	11
16	4	11
17	5	12
18	2	13
19	5	14
20	2	15
21	5	16
22	2	17
23	5	18
24	2	19
25	5	20
26	3	23
27	2	23
28	1	23
29	4	23
30	5	23
31	5	24
32	2	25
33	5	25
34	2	26
35	5	26
36	3	27
37	2	27
38	1	27
39	4	27
40	5	27
41	5	28
42	3	29
43	2	29
44	1	29
45	4	29
46	5	29
47	2	30
48	5	30
49	2	31
50	5	31
51	2	32
52	5	32
53	3	33
54	2	33
55	1	33
56	4	33
57	5	33
58	2	34
59	5	34
60	6	34
61	7	34
62	8	34
63	9	34
64	10	34
65	2	35
66	5	35
67	2	36
68	5	36
69	3	37
70	2	37
71	1	37
72	4	37
73	5	37
74	3	38
75	2	38
76	4	38
77	5	38
78	5	40
79	5	42
80	5	43
81	5	44
82	5	45
83	2	42
84	1	42
85	4	42
86	2	43
87	2	46
88	2	47
89	2	48
90	2	40
91	2	49
92	2	50
93	4	51
94	2	51
95	1	51
96	4	52
97	2	52
98	1	52
99	4	53
100	2	53
101	1	53
102	4	54
103	4	55
104	2	55
105	2	54
106	1	55
107	1	54
108	4	56
109	2	56
110	1	56
\.


--
-- Data for Name: ab_permission_view_role; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_permission_view_role (id, permission_view_id, role_id) FROM stdin;
1	1	1
2	2	1
3	3	1
4	4	1
5	5	1
6	6	1
7	7	1
8	8	1
9	9	1
10	10	1
11	11	1
12	12	1
13	13	1
14	14	1
15	15	1
16	16	1
17	17	1
18	18	1
19	19	1
20	20	1
21	21	1
22	22	1
23	23	1
24	24	1
25	25	1
26	26	1
27	27	1
28	28	1
29	29	1
30	30	1
31	31	1
32	32	1
33	33	1
34	34	1
35	35	1
36	36	1
37	37	1
38	38	1
39	39	1
40	40	1
41	41	1
42	42	1
43	43	1
44	44	1
45	45	1
46	46	1
47	47	1
48	48	1
49	49	1
50	50	1
51	51	1
52	52	1
53	53	1
54	54	1
55	55	1
56	56	1
57	57	1
58	58	1
59	59	1
60	60	1
61	61	1
62	62	1
63	63	1
64	64	1
65	65	1
66	66	1
67	67	1
68	68	1
69	69	1
70	70	1
71	71	1
72	72	1
73	73	1
74	74	1
75	75	1
76	76	1
77	77	1
78	78	1
79	79	1
80	80	1
81	81	1
82	82	1
83	34	3
84	83	3
85	90	3
86	88	3
87	27	3
88	86	3
89	87	3
90	89	3
91	32	3
92	4	3
93	3	3
94	6	3
95	5	3
96	65	3
97	58	3
98	43	3
99	91	3
100	75	3
101	92	3
102	31	3
103	79	3
104	78	3
105	30	3
106	80	3
107	81	3
108	82	3
109	33	3
110	35	3
111	66	3
112	59	3
113	46	3
114	34	4
115	83	4
116	90	4
117	88	4
118	27	4
119	86	4
120	87	4
121	89	4
122	32	4
123	4	4
124	3	4
125	6	4
126	5	4
127	65	4
128	58	4
129	43	4
130	91	4
131	75	4
132	92	4
133	31	4
134	79	4
135	78	4
136	30	4
137	80	4
138	81	4
139	82	4
140	33	4
141	35	4
142	66	4
143	59	4
144	46	4
145	84	4
146	85	4
147	42	4
148	44	4
149	45	4
150	26	4
151	28	4
152	29	4
153	34	5
154	83	5
155	90	5
156	88	5
157	27	5
158	86	5
159	87	5
160	89	5
161	32	5
162	4	5
163	3	5
164	6	5
165	5	5
166	65	5
167	58	5
168	43	5
169	91	5
170	75	5
171	92	5
172	31	5
173	79	5
174	78	5
175	30	5
176	80	5
177	81	5
178	82	5
179	33	5
180	35	5
181	66	5
182	59	5
183	46	5
184	84	5
185	85	5
186	42	5
187	44	5
188	45	5
189	26	5
190	28	5
191	29	5
192	51	5
193	41	5
194	52	5
195	57	5
196	73	5
197	40	5
198	77	5
199	53	5
200	54	5
201	55	5
202	56	5
203	69	5
204	70	5
205	71	5
206	72	5
207	67	5
208	36	5
209	37	5
210	38	5
211	39	5
212	76	5
213	83	1
214	90	1
215	88	1
216	86	1
217	87	1
218	89	1
219	91	1
220	92	1
221	84	1
222	85	1
\.


--
-- Data for Name: ab_register_user; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_register_user (id, first_name, last_name, username, password, email, registration_date, registration_hash) FROM stdin;
\.


--
-- Data for Name: ab_role; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_role (id, name) FROM stdin;
1	Admin
2	Public
3	Viewer
4	User
5	Op
\.


--
-- Data for Name: ab_user; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_user (id, first_name, last_name, username, password, active, email, last_login, login_count, fail_login_count, created_on, changed_on, created_by_fk, changed_by_fk) FROM stdin;
1	Airflow	Admin	airflow	pbkdf2:sha256:260000$1nOF3USsxjIWtmlZ$f36a68d19ee0c4b6fe222ed1eb81419d84646a7dbb0daada706fc210f5386e9d	t	airflow@airflow.com	2025-04-24 20:47:27.715066	3	0	2025-04-24 20:15:54.39728	2025-04-24 20:15:54.397287	\N	\N
\.


--
-- Data for Name: ab_user_role; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_user_role (id, user_id, role_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: ab_view_menu; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.ab_view_menu (id, name) FROM stdin;
1	IndexView
2	UtilView
3	LocaleView
4	Passwords
5	My Password
6	My Profile
7	AuthDBView
8	Users
9	List Users
10	Security
11	Roles
12	List Roles
13	User Stats Chart
14	User's Statistics
15	Permissions
16	Actions
17	View Menus
18	Resources
19	Permission Views
20	Permission Pairs
21	AutocompleteView
22	Airflow
23	DAG Runs
24	Browse
25	Jobs
26	Audit Logs
27	Variables
28	Admin
29	Task Instances
30	Task Reschedules
31	Triggers
32	Configurations
33	Connections
34	SLA Misses
35	Plugins
36	Providers
37	Pools
38	XComs
39	DagDependenciesView
40	DAG Dependencies
41	RedocView
42	DAGs
43	Datasets
44	Documentation
45	Docs
46	ImportError
47	DAG Code
48	DAG Warnings
49	Task Logs
50	Website
51	DAG:project_trading_daily_sync
52	DAG:market_analysis_ingestion
53	DAG:project_analytics_client1_reporting
54	DAG:common_system_maintenance
55	DAG:project_analytics_client3_reporting
56	DAG:project_analytics_client2_reporting
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.alembic_version (version_num) FROM stdin;
98ae134e6fff
\.


--
-- Data for Name: callback_request; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.callback_request (id, created_at, priority_weight, callback_data, callback_type, processor_subdir) FROM stdin;
\.


--
-- Data for Name: connection; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.connection (id, conn_id, conn_type, description, host, schema, login, password, port, is_encrypted, is_extra_encrypted, extra) FROM stdin;
1	airflow_db	mysql	\N	mysql	airflow	root	\N	\N	f	f	\N
2	aws_default	aws	\N	\N	\N	\N	\N	\N	f	f	\N
3	azure_batch_default	azure_batch	\N	\N	\N	<ACCOUNT_NAME>	\N	\N	f	f	{"account_url": "<ACCOUNT_URL>"}
4	azure_cosmos_default	azure_cosmos	\N	\N	\N	\N	\N	\N	f	f	{"database_name": "<DATABASE_NAME>", "collection_name": "<COLLECTION_NAME>" }
5	azure_data_explorer_default	azure_data_explorer	\N	https://<CLUSTER>.kusto.windows.net	\N	\N	\N	\N	f	f	{"auth_method": "<AAD_APP | AAD_APP_CERT | AAD_CREDS | AAD_DEVICE>",\n                    "tenant": "<TENANT ID>", "certificate": "<APPLICATION PEM CERTIFICATE>",\n                    "thumbprint": "<APPLICATION CERTIFICATE THUMBPRINT>"}
6	azure_data_lake_default	azure_data_lake	\N	\N	\N	\N	\N	\N	f	f	{"tenant": "<TENANT>", "account_name": "<ACCOUNTNAME>" }
7	azure_default	azure	\N	\N	\N	\N	\N	\N	f	f	\N
8	cassandra_default	cassandra	\N	cassandra	\N	\N	\N	9042	f	f	\N
9	databricks_default	databricks	\N	localhost	\N	\N	\N	\N	f	f	\N
10	dingding_default	http	\N		\N	\N	\N	\N	f	f	\N
11	drill_default	drill	\N	localhost	\N	\N	\N	8047	f	f	{"dialect_driver": "drill+sadrill", "storage_plugin": "dfs"}
12	druid_broker_default	druid	\N	druid-broker	\N	\N	\N	8082	f	f	{"endpoint": "druid/v2/sql"}
13	druid_ingest_default	druid	\N	druid-overlord	\N	\N	\N	8081	f	f	{"endpoint": "druid/indexer/v1/task"}
14	elasticsearch_default	elasticsearch	\N	localhost	http	\N	\N	9200	f	f	\N
15	emr_default	emr	\N	\N	\N	\N	\N	\N	f	f	\n                {   "Name": "default_job_flow_name",\n                    "LogUri": "s3://my-emr-log-bucket/default_job_flow_location",\n                    "ReleaseLabel": "emr-4.6.0",\n                    "Instances": {\n                        "Ec2KeyName": "mykey",\n                        "Ec2SubnetId": "somesubnet",\n                        "InstanceGroups": [\n                            {\n                                "Name": "Master nodes",\n                                "Market": "ON_DEMAND",\n                                "InstanceRole": "MASTER",\n                                "InstanceType": "r3.2xlarge",\n                                "InstanceCount": 1\n                            },\n                            {\n                                "Name": "Core nodes",\n                                "Market": "ON_DEMAND",\n                                "InstanceRole": "CORE",\n                                "InstanceType": "r3.2xlarge",\n                                "InstanceCount": 1\n                            }\n                        ],\n                        "TerminationProtected": false,\n                        "KeepJobFlowAliveWhenNoSteps": false\n                    },\n                    "Applications":[\n                        { "Name": "Spark" }\n                    ],\n                    "VisibleToAllUsers": true,\n                    "JobFlowRole": "EMR_EC2_DefaultRole",\n                    "ServiceRole": "EMR_DefaultRole",\n                    "Tags": [\n                        {\n                            "Key": "app",\n                            "Value": "analytics"\n                        },\n                        {\n                            "Key": "environment",\n                            "Value": "development"\n                        }\n                    ]\n                }\n            
16	facebook_default	facebook_social	\N	\N	\N	\N	\N	\N	f	f	\n                {   "account_id": "<AD_ACCOUNT_ID>",\n                    "app_id": "<FACEBOOK_APP_ID>",\n                    "app_secret": "<FACEBOOK_APP_SECRET>",\n                    "access_token": "<FACEBOOK_AD_ACCESS_TOKEN>"\n                }\n            
17	fs_default	fs	\N	\N	\N	\N	\N	\N	f	f	{"path": "/"}
18	ftp_default	ftp	\N	localhost	\N	airflow	airflow	21	f	f	{"key_file": "~/.ssh/id_rsa", "no_host_key_check": true}
19	google_cloud_default	google_cloud_platform	\N	\N	default	\N	\N	\N	f	f	\N
20	hive_cli_default	hive_cli	\N	localhost	default	\N	\N	10000	f	f	{"use_beeline": true, "auth": ""}
21	hiveserver2_default	hiveserver2	\N	localhost	default	\N	\N	10000	f	f	\N
22	http_default	http	\N	https://www.httpbin.org/	\N	\N	\N	\N	f	f	\N
23	impala_default	impala	\N	localhost	\N	\N	\N	21050	f	f	\N
24	kubernetes_default	kubernetes	\N	\N	\N	\N	\N	\N	f	f	\N
25	kylin_default	kylin	\N	localhost	\N	ADMIN	KYLIN	7070	f	f	\N
26	leveldb_default	leveldb	\N	localhost	\N	\N	\N	\N	f	f	\N
27	livy_default	livy	\N	livy	\N	\N	\N	8998	f	f	\N
28	local_mysql	mysql	\N	localhost	airflow	airflow	airflow	\N	f	f	\N
29	metastore_default	hive_metastore	\N	localhost	\N	\N	\N	9083	f	f	{"authMechanism": "PLAIN"}
30	mongo_default	mongo	\N	mongo	\N	\N	\N	27017	f	f	\N
31	mssql_default	mssql	\N	localhost	\N	\N	\N	1433	f	f	\N
32	mysql_default	mysql	\N	mysql	airflow	root	\N	\N	f	f	\N
33	opsgenie_default	http	\N		\N	\N	\N	\N	f	f	\N
34	oracle_default	oracle	\N	localhost	schema	root	password	1521	f	f	\N
35	oss_default	oss	\N	\N	\N	\N	\N	\N	f	f	{\n                "auth_type": "AK",\n                "access_key_id": "<ACCESS_KEY_ID>",\n                "access_key_secret": "<ACCESS_KEY_SECRET>",\n                "region": "<YOUR_OSS_REGION>"}\n                
36	pig_cli_default	pig_cli	\N	\N	default	\N	\N	\N	f	f	\N
37	pinot_admin_default	pinot	\N	localhost	\N	\N	\N	9000	f	f	\N
38	pinot_broker_default	pinot	\N	localhost	\N	\N	\N	9000	f	f	{"endpoint": "/query", "schema": "http"}
39	postgres_default	postgres	\N	postgres	airflow	postgres	airflow	\N	f	f	\N
40	presto_default	presto	\N	localhost	hive	\N	\N	3400	f	f	\N
41	qubole_default	qubole	\N	localhost	\N	\N	\N	\N	f	f	\N
42	redis_default	redis	\N	redis	\N	\N	\N	6379	f	f	{"db": 0}
43	redshift_default	redshift	\N	\N	\N	\N	\N	\N	f	f	{\n    "iam": true,\n    "cluster_identifier": "<REDSHIFT_CLUSTER_IDENTIFIER>",\n    "port": 5439,\n    "profile": "default",\n    "db_user": "awsuser",\n    "database": "dev",\n    "region": ""\n}
44	salesforce_default	salesforce	\N	\N	\N	username	password	\N	f	f	{"security_token": "security_token"}
45	segment_default	segment	\N	\N	\N	\N	\N	\N	f	f	{"write_key": "my-segment-write-key"}
46	sftp_default	sftp	\N	localhost	\N	airflow	\N	22	f	f	{"key_file": "~/.ssh/id_rsa", "no_host_key_check": true}
47	spark_default	spark	\N	yarn	\N	\N	\N	\N	f	f	{"queue": "root.default"}
48	sqlite_default	sqlite	\N	/tmp/sqlite_default.db	\N	\N	\N	\N	f	f	\N
49	sqoop_default	sqoop	\N	rdbms	\N	\N	\N	\N	f	f	\N
50	ssh_default	ssh	\N	localhost	\N	\N	\N	\N	f	f	\N
51	tableau_default	tableau	\N	https://tableau.server.url	\N	user	password	\N	f	f	{"site_id": "my_site"}
52	tabular_default	tabular	\N	https://api.tabulardata.io/ws/v1	\N	\N	\N	\N	f	f	\N
53	trino_default	trino	\N	localhost	hive	\N	\N	3400	f	f	\N
54	vertica_default	vertica	\N	localhost	\N	\N	\N	5433	f	f	\N
55	wasb_default	wasb	\N	\N	\N	\N	\N	\N	f	f	{"sas_token": null}
56	webhdfs_default	hdfs	\N	localhost	\N	\N	\N	50070	f	f	\N
57	yandexcloud_default	yandexcloud	\N	\N	default	\N	\N	\N	f	f	\N
\.


--
-- Data for Name: dag; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag (dag_id, root_dag_id, is_paused, is_subdag, is_active, last_parsed_time, last_pickled, last_expired, scheduler_lock, pickle_id, fileloc, processor_subdir, owners, description, default_view, schedule_interval, timetable_description, max_active_tasks, max_active_runs, has_task_concurrency_limits, has_import_errors, next_dagrun, next_dagrun_data_interval_start, next_dagrun_data_interval_end, next_dagrun_create_after) FROM stdin;
market_analysis_ingestion	\N	f	f	t	2025-04-25 16:48:12.786227+00	\N	\N	\N	\N	/opt/airflow/dags/market-analysis/dag_market_analysis_ingestion.py	/opt/airflow/dags	analytics_team	Ingest market data via market-analysis container	grid	"@daily"	At 00:00	16	16	f	f	2025-04-25 00:00:00+00	2025-04-25 00:00:00+00	2025-04-26 00:00:00+00	2025-04-26 00:00:00+00
project_trading_daily_sync	\N	t	f	t	2025-04-25 16:48:12.878503+00	\N	\N	\N	\N	/opt/airflow/dags/project_trading/trading_daily_sync.py	/opt/airflow/dags	trading_team	Syncs daily trading data from IBKR to data warehouse	grid	"0 1 * * *"	At 01:00	16	16	f	f	2025-04-24 01:00:00+00	2025-04-24 01:00:00+00	2025-04-25 01:00:00+00	2025-04-25 01:00:00+00
project_analytics_client1_reporting	\N	t	f	t	2025-04-25 16:48:12.897907+00	\N	\N	\N	\N	/opt/airflow/dags/project_analytics/client_reporting_factory.py	/opt/airflow/dags	analytics_team	Daily reporting for client1	grid	"0 6 * * *"	At 06:00	16	16	f	f	2025-04-24 06:00:00+00	2025-04-24 06:00:00+00	2025-04-25 06:00:00+00	2025-04-25 06:00:00+00
project_analytics_client2_reporting	\N	t	f	t	2025-04-25 16:48:12.901258+00	\N	\N	\N	\N	/opt/airflow/dags/project_analytics/client_reporting_factory.py	/opt/airflow/dags	analytics_team	Daily reporting for client2	grid	"0 7 * * *"	At 07:00	16	16	f	f	2025-04-24 07:00:00+00	2025-04-24 07:00:00+00	2025-04-25 07:00:00+00	2025-04-25 07:00:00+00
project_analytics_client3_reporting	\N	t	f	t	2025-04-25 16:48:12.90524+00	\N	\N	\N	\N	/opt/airflow/dags/project_analytics/client_reporting_factory.py	/opt/airflow/dags	analytics_team	Daily reporting for client3	grid	"0 8 * * 1-5"	At 08:00, Monday through Friday	16	16	f	f	2025-04-24 08:00:00+00	2025-04-24 08:00:00+00	2025-04-25 08:00:00+00	2025-04-25 08:00:00+00
common_system_maintenance	\N	t	f	t	2025-04-25 16:48:13.016851+00	\N	\N	\N	\N	/opt/airflow/dags/common/system_maintenance.py	/opt/airflow/dags	airflow_admin	System-wide maintenance tasks	grid	"0 0 * * 0"	At 00:00, only on Sunday	16	16	f	f	2025-04-27 00:00:00+00	2025-04-27 00:00:00+00	2025-05-04 00:00:00+00	2025-05-04 00:00:00+00
\.


--
-- Data for Name: dag_code; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_code (fileloc_hash, fileloc, last_updated, source_code) FROM stdin;
48767742691821281	/opt/airflow/dags/project_trading/trading_daily_sync.py	2025-04-24 20:14:14.031945+00	"""\nDaily trading data synchronization DAG.\n\nThis DAG extracts trading data from Interactive Brokers, processes it,\nand loads it into a data warehouse for analysis.\n"""\n\nfrom airflow import DAG\nfrom airflow.utils.dates import days_ago\nfrom airflow.providers.docker.operators.docker import DockerOperator\nfrom airflow.providers.snowflake.operators.snowflake import SnowflakeOperator\nfrom plugins.project_trading.operators import IBKRDataOperator\n\n# Configuration with project-specific naming conventions\nDEFAULT_ARGS = {\n    'owner': 'trading_team',\n    'depends_on_past': False,\n    'retries': 3,\n    'retry_delay': 300,  # 5 minutes\n    'pool': 'project_trading_pool',  # Project-specific resource pool\n}\n\n# DAG ID has project prefix for clear identification\ndag = DAG(\n    'project_trading_daily_sync',\n    default_args=DEFAULT_ARGS,\n    description='Syncs daily trading data from IBKR to data warehouse',\n    schedule_interval='0 1 * * *',  # 1:00 AM daily\n    start_date=days_ago(1),\n    tags=['trading', 'ibkr'],\n)\n# Use module docstring as DAG documentation\ndag.doc_md = __doc__\n\n# Extract task now uses DockerOperator for full dependency isolation and reproducibility.\n# This runs the new extract_ibkr_data.py CLI script inside the project_trading container.\nextract_task = DockerOperator(\n    task_id='extract_ibkr_data',\n    image='project_trading:latest',  # Image built from Dockerfile.project_trading\n    command=[\n        'python', '/app/plugins/project_trading/extract_ibkr_data.py',\n        '--conn-id', 'project_trading_ibkr',\n        '--data-types', 'trades', 'positions', 'market_data',\n        '--start-date', '{{ ds }}',\n        '--end-date', '{{ ds }}',\n        '--output-path', '/tmp/data/{{ ds }}',\n    ],\n    environment={\n        # Pass any secrets/credentials via env or Docker secrets in production\n    },\n    docker_url='unix://var/run/docker.sock',\n    network_mode='bridge',\n    dag=dag,\n)\n\n# Processing task using containerized execution for dependency isolation\nprocess_task = DockerOperator(\n    task_id='process_trading_data',\n    image='trading-project:latest',\n    command='python /scripts/process_trading_data.py',\n    environment={\n        'DATA_DATE': '{{ ds }}',\n        'DATA_PATH': '/tmp/data/{{ ds }}',\n    },\n    docker_url='unix://var/run/docker.sock',\n    network_mode='bridge',\n    dag=dag,\n)\n\n# Data load task with project-specific connection\nload_task = SnowflakeOperator(\n    task_id='load_processed_data',\n    snowflake_conn_id='project_trading_snowflake',\n    sql='CALL trading.load_daily_data(\\'{{ ds }}\\')',\n    dag=dag,\n)\n\n# Define simple linear flow\nextract_task >> process_task >> load_task\n
43921834427787191	/opt/airflow/dags/common/system_maintenance.py	2025-04-24 20:14:14.697073+00	"""\nSystem maintenance DAG.\n\nThis DAG performs system-wide maintenance tasks that affect all projects,\nsuch as log cleanup, database optimization, and health checks.\n"""\n\nfrom airflow import DAG\nfrom airflow.operators.bash import BashOperator\nfrom airflow.operators.python import PythonOperator\nfrom airflow.utils.dates import days_ago\nfrom datetime import timedelta\n\n# Configuration for system maintenance\nDEFAULT_ARGS = {\n    'owner': 'airflow_admin',\n    'depends_on_past': False,\n    'retries': 1,\n    'retry_delay': timedelta(minutes=5),\n    'email_on_failure': True,\n    'email': ['admin@example.com'],\n}\n\n# DAG ID uses 'common' prefix to indicate it's a shared DAG\ndag = DAG(\n    'common_system_maintenance',\n    default_args=DEFAULT_ARGS,\n    description='System-wide maintenance tasks',\n    schedule_interval='0 0 * * 0',  # Weekly at midnight on Sunday\n    start_date=days_ago(1),\n    tags=['maintenance', 'system', 'common'],\n)\n# Use module docstring as DAG documentation\ndag.doc_md = __doc__\n\n# Task to clean up old logs\ncleanup_logs = BashOperator(\n    task_id='cleanup_old_logs',\n    bash_command='find /opt/airflow/logs -type f -name "*.log" -mtime +30 -delete',\n    dag=dag,\n)\n\n# Task to optimize Airflow database\noptimize_db = BashOperator(\n    task_id='optimize_airflow_db',\n    bash_command='airflow db clean --clean-before-timestamp "$(date -d "-30 days" "+%Y-%m-%d")"',\n    dag=dag,\n)\n\ndef check_disk_space(**kwargs):\n    """\n    Check disk space and log warning if below threshold.\n    """\n    import os\n    import logging\n    \n    logger = logging.getLogger(__name__)\n    threshold_gb = 10  # Minimum required disk space in GB\n    \n    # Get disk usage statistics\n    stat = os.statvfs('/opt/airflow')\n    free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)\n    \n    if free_gb < threshold_gb:\n        logger.warning(f"Low disk space: {free_gb:.2f} GB free, threshold is {threshold_gb} GB")\n        kwargs['ti'].xcom_push(key='disk_space_warning', value=True)\n        return False\n    else:\n        logger.info(f"Disk space check passed: {free_gb:.2f} GB free")\n        return True\n\n# Task to check disk space\ncheck_disk = PythonOperator(\n    task_id='check_disk_space',\n    python_callable=check_disk_space,\n    dag=dag,\n)\n\ndef check_connections(**kwargs):\n    """\n    Check all connections are valid and log any issues.\n    """\n    import logging\n    from airflow.hooks.base import BaseHook\n    \n    logger = logging.getLogger(__name__)\n    connections = BaseHook.get_connections()\n    \n    failed_connections = []\n    \n    for conn in connections:\n        try:\n            # Try to get the connection (this will validate it)\n            hook = BaseHook.get_hook(conn_id=conn.conn_id)\n            logger.info(f"Connection {conn.conn_id} is valid")\n        except Exception as e:\n            logger.warning(f"Connection {conn.conn_id} failed validation: {str(e)}")\n            failed_connections.append(conn.conn_id)\n    \n    if failed_connections:\n        kwargs['ti'].xcom_push(key='failed_connections', value=failed_connections)\n        return False\n    else:\n        return True\n\n# Task to check connections\ncheck_connections_task = PythonOperator(\n    task_id='check_connections',\n    python_callable=check_connections,\n    dag=dag,\n)\n\n# Define task dependencies\ncleanup_logs >> optimize_db\ncheck_disk >> check_connections_task\n
61179450594028497	/opt/airflow/dags/project_analytics/client_reporting_factory.py	2025-04-24 20:14:14.730762+00	"""\nClient reporting DAG factory.\n\nThis module demonstrates the DAG factory pattern for generating multiple similar DAGs,\none for each client's reporting needs. This approach avoids code duplication while\nmaintaining clear separation between client-specific workflows.\n"""\n\nfrom airflow import DAG\nfrom airflow.utils.dates import days_ago\nfrom airflow.providers.snowflake.operators.snowflake import SnowflakeOperator\nfrom airflow.operators.python import PythonOperator\nfrom datetime import datetime, timedelta\n\n# Client configuration\nCLIENTS = {\n    'client1': {\n        'schedule': '0 6 * * *',  # 6:00 AM daily\n        'start_date': days_ago(1),\n        'email': 'client1@example.com',\n        'report_types': ['summary', 'detailed', 'forecast']\n    },\n    'client2': {\n        'schedule': '0 7 * * *',  # 7:00 AM daily\n        'start_date': days_ago(1),\n        'email': 'client2@example.com',\n        'report_types': ['summary', 'detailed']\n    },\n    'client3': {\n        'schedule': '0 8 * * 1-5',  # 8:00 AM weekdays only\n        'start_date': days_ago(1),\n        'email': 'client3@example.com',\n        'report_types': ['summary']\n    }\n}\n\n# Default arguments for all client DAGs\nDEFAULT_ARGS = {\n    'owner': 'analytics_team',\n    'depends_on_past': False,\n    'retries': 2,\n    'retry_delay': timedelta(minutes=5),\n    'pool': 'project_analytics_pool',\n    'email_on_failure': True,\n    'email_on_retry': False,\n}\n\ndef send_email_notification(client_id, report_date, report_types, recipient_email, **kwargs):\n    """\n    Send email notification when reports are ready.\n    \n    In a real implementation, this would use Airflow's email functionality or an API.\n    For this example, we'll just log the action.\n    """\n    import logging\n    logger = logging.getLogger(__name__)\n    \n    logger.info(f"Sending email notification to {recipient_email}")\n    logger.info(f"Reports ready for {client_id} for date {report_date}: {', '.join(report_types)}")\n    \n    # In a real implementation:\n    # from airflow.utils.email import send_email\n    # send_email(\n    #     to=recipient_email,\n    #     subject=f"Reports Ready: {client_id} - {report_date}",\n    #     html_content=f"Your reports are ready: {', '.join(report_types)}",\n    # )\n    \n    return True\n\ndef create_client_dag(client_id, config):\n    """\n    Create a DAG for a specific client's reporting needs.\n    \n    Args:\n        client_id (str): Client identifier.\n        config (dict): Client-specific configuration.\n        \n    Returns:\n        DAG: Configured Airflow DAG for this client.\n    """\n    dag_id = f"project_analytics_{client_id}_reporting"\n    \n    dag = DAG(\n        dag_id,\n        default_args={**DEFAULT_ARGS, 'email': [config['email']]},\n        description=f"Daily reporting for {client_id}",\n        schedule_interval=config['schedule'],\n        start_date=config['start_date'],\n        tags=['analytics', 'reporting', client_id],\n    )\n# Use module docstring for DAG documentation\n    dag.doc_md = __doc__\n    \n    # Generate reports task\n    generate_reports = SnowflakeOperator(\n        task_id='generate_client_reports',\n        snowflake_conn_id='project_analytics_snowflake',\n        sql=f'''\n        -- Generate client-specific reports\n        CALL analytics.generate_client_reports(\n            '{client_id}',\n            '{{{{ ds }}}}',\n            '{",".join(config["report_types"])}'\n        );\n        ''',\n        dag=dag,\n    )\n    \n    # Export reports task\n    export_reports = SnowflakeOperator(\n        task_id='export_reports_to_storage',\n        snowflake_conn_id='project_analytics_snowflake',\n        sql=f'''\n        -- Export reports to cloud storage\n        CALL analytics.export_client_reports_to_storage(\n            '{client_id}',\n            '{{{{ ds }}}}'\n        );\n        ''',\n        dag=dag,\n    )\n    \n    # Send notification task\n    send_notification = PythonOperator(\n        task_id='send_email_notification',\n        python_callable=send_email_notification,\n        op_kwargs={\n            'client_id': client_id,\n            'report_date': '{{ ds }}',\n            'report_types': config['report_types'],\n            'recipient_email': config['email']\n        },\n        dag=dag,\n    )\n    \n    # Define task dependencies\n    generate_reports >> export_reports >> send_notification\n    \n    return dag\n\n# Create a DAG for each client\nfor client_id, config in CLIENTS.items():\n    globals()[f"{client_id}_dag"] = create_client_dag(client_id, config)\n
6932960973159084	/opt/airflow/dags/market-analysis/dag_market_analysis_ingestion.py	2025-04-24 20:51:27.761428+00	"""\nMarket Analysis Ingestion DAG.\n\nThis DAG uses the `market-analysis:latest` Docker image to fetch daily market data\nfor a specified symbol and date using the market-analysis script.\n\nIt requires the Airflow Variables `binance_api_key` and `binance_secret_key` to be set,\nwhich contain the necessary credentials for the Binance API. These variables are\npassed as environment variables to the Docker container run by the `DockerOperator`.\n"""\nfrom airflow import DAG\nfrom airflow.providers.docker.operators.docker import DockerOperator\nfrom airflow.utils.dates import days_ago\nfrom datetime import timedelta\n\n# Default arguments for the DAG\nDEFAULT_ARGS = {\n    'owner': 'analytics_team',\n    'depends_on_past': False,\n    'retries': 2,\n    'retry_delay': timedelta(minutes=5),\n    'pool': 'project_market_analysis_pool',\n}\n\n# Define the DAG\ndag = DAG(\n    'market_analysis_ingestion',\n    default_args=DEFAULT_ARGS,\n    description='Ingest market data via market-analysis container',\n    schedule_interval='@daily',\n    start_date=days_ago(1),\n    tags=['market-analysis', 'ingestion'],\n)\n# Use module docstring in Airflow UI\ndag.doc_md = __doc__\n\n# Task: Run the ingestion script in the Docker container\ningest_task = DockerOperator(\n    task_id='ingest_market_data',\n    image='market-analysis:latest',\n    # Pass Airflow Variables (sourced from .env via docker-compose) to the container\n    environment={\n        'BINANCE_API_KEY': '{{ var.value.binance_api_key }}',\n        'BINANCE_SECRET_KEY': '{{ var.value.binance_secret_key }}'\n    },\n    command=[\n        'python', '-m', 'src.main',\n        '--symbol', '{{ params.symbol }}',\n        '--start', '{{ ds }}',\n        '--end', '{{ ds }}',\n    ],\n    params={'symbol': 'AAPL'},\n    docker_url='unix://var/run/docker.sock',\n    network_mode='bridge',\n    execution_timeout=timedelta(minutes=30),\n    dag=dag,\n)
\.


--
-- Data for Name: dag_owner_attributes; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_owner_attributes (dag_id, owner, link) FROM stdin;
\.


--
-- Data for Name: dag_pickle; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_pickle (id, pickle, created_dttm, pickle_hash) FROM stdin;
\.


--
-- Data for Name: dag_run; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_run (id, dag_id, queued_at, execution_date, start_date, end_date, state, run_id, creating_job_id, external_trigger, run_type, conf, data_interval_start, data_interval_end, last_scheduling_decision, dag_hash, log_template_id, updated_at) FROM stdin;
1	market_analysis_ingestion	2025-04-24 20:44:30.51059+00	2025-04-24 20:44:30.482568+00	2025-04-24 20:44:30.975573+00	\N	running	manual__2025-04-24T20:44:30.482568+00:00	\N	t	manual	\\x80047d942e	2025-04-23 00:00:00+00	2025-04-24 00:00:00+00	2025-04-25 16:48:31.471553+00	626d9716205f99f36ab9ed93cee8c7ed	2	2025-04-25 16:48:31.472961+00
2	market_analysis_ingestion	2025-04-24 20:44:30.952248+00	2025-04-23 00:00:00+00	2025-04-24 20:44:30.975211+00	\N	running	scheduled__2025-04-23T00:00:00+00:00	2	f	scheduled	\\x80047d942e	2025-04-23 00:00:00+00	2025-04-24 00:00:00+00	2025-04-25 16:48:31.468759+00	626d9716205f99f36ab9ed93cee8c7ed	2	2025-04-25 16:48:31.472967+00
3	market_analysis_ingestion	2025-04-25 12:46:53.725283+00	2025-04-24 00:00:00+00	2025-04-25 12:46:53.76128+00	\N	running	scheduled__2025-04-24T00:00:00+00:00	4	f	scheduled	\\x80047d942e	2025-04-24 00:00:00+00	2025-04-25 00:00:00+00	2025-04-25 16:48:31.465989+00	626d9716205f99f36ab9ed93cee8c7ed	2	2025-04-25 16:48:31.47297+00
\.


--
-- Data for Name: dag_run_note; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_run_note (user_id, dag_run_id, content, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dag_schedule_dataset_reference; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_schedule_dataset_reference (dataset_id, dag_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dag_tag; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_tag (name, dag_id) FROM stdin;
ibkr	project_trading_daily_sync
trading	project_trading_daily_sync
ingestion	market_analysis_ingestion
market-analysis	market_analysis_ingestion
system	common_system_maintenance
maintenance	common_system_maintenance
common	common_system_maintenance
analytics	project_analytics_client1_reporting
client1	project_analytics_client1_reporting
reporting	project_analytics_client1_reporting
analytics	project_analytics_client2_reporting
client2	project_analytics_client2_reporting
reporting	project_analytics_client2_reporting
analytics	project_analytics_client3_reporting
client3	project_analytics_client3_reporting
reporting	project_analytics_client3_reporting
\.


--
-- Data for Name: dag_warning; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dag_warning (dag_id, warning_type, message, "timestamp") FROM stdin;
project_trading_daily_sync	non-existent pool	Dag 'project_trading_daily_sync' references non-existent pools: ['project_trading_pool']	2025-04-24 20:14:14.056037+00
market_analysis_ingestion	non-existent pool	Dag 'market_analysis_ingestion' references non-existent pools: ['project_market_analysis_pool']	2025-04-24 20:14:14.079483+00
project_analytics_client1_reporting	non-existent pool	Dag 'project_analytics_client1_reporting' references non-existent pools: ['project_analytics_pool']	2025-04-24 20:14:14.747111+00
project_analytics_client3_reporting	non-existent pool	Dag 'project_analytics_client3_reporting' references non-existent pools: ['project_analytics_pool']	2025-04-24 20:14:14.747121+00
project_analytics_client2_reporting	non-existent pool	Dag 'project_analytics_client2_reporting' references non-existent pools: ['project_analytics_pool']	2025-04-24 20:14:14.747127+00
\.


--
-- Data for Name: dagrun_dataset_event; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dagrun_dataset_event (dag_run_id, event_id) FROM stdin;
\.


--
-- Data for Name: dataset; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dataset (id, uri, extra, created_at, updated_at, is_orphaned) FROM stdin;
\.


--
-- Data for Name: dataset_dag_run_queue; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dataset_dag_run_queue (dataset_id, target_dag_id, created_at) FROM stdin;
\.


--
-- Data for Name: dataset_event; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.dataset_event (id, dataset_id, extra, source_task_id, source_dag_id, source_run_id, source_map_index, "timestamp") FROM stdin;
\.


--
-- Data for Name: import_error; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.import_error (id, "timestamp", filename, stacktrace) FROM stdin;
1	2025-04-25 16:48:12.771552+00	/opt/airflow/dags/project_analytics/analytics_daily_etl.py	Traceback (most recent call last):\n  File "/opt/airflow/plugins/common/operators/base_operator.py", line 33, in __init__\n    self.log = logging.getLogger(__name__)\n  File "/home/airflow/.local/lib/python3.7/site-packages/airflow/models/baseoperator.py", line 1056, in __setattr__\n    super().__setattr__(key, value)\nAttributeError: can't set attribute\n
\.


--
-- Data for Name: job; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.job (id, dag_id, state, job_type, start_date, end_date, latest_heartbeat, executor_class, hostname, unixname) FROM stdin;
4	\N	running	SchedulerJob	2025-04-25 12:46:53.289013+00	\N	2025-04-25 16:48:23.605666+00	LocalExecutor	6ca8332e5db9	airflow
1	\N	success	SchedulerJob	2025-04-24 20:14:12.968835+00	2025-04-24 20:32:22.264748+00	2025-04-24 20:32:15.846464+00	LocalExecutor	6b1fe676c3a8	airflow
3	\N	failed	SchedulerJob	2025-04-24 20:47:15.34987+00	\N	2025-04-24 21:01:03.289111+00	LocalExecutor	6ca8332e5db9	airflow
2	\N	success	SchedulerJob	2025-04-24 20:41:31.277512+00	2025-04-24 20:46:53.351033+00	2025-04-24 20:46:49.238837+00	LocalExecutor	6d50aafebeb6	airflow
\.


--
-- Data for Name: log; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.log (id, dttm, dag_id, task_id, map_index, event, execution_date, owner, extra) FROM stdin;
1	2025-04-24 20:13:59.302751+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "056fbd958996", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
2	2025-04-24 20:13:59.880932+00	\N	\N	\N	cli_webserver	\N	airflow	{"host_name": "056fbd958996", "full_command": "['/home/airflow/.local/bin/airflow', 'webserver']"}
3	2025-04-24 20:14:08.079749+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "6b1fe676c3a8", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
4	2025-04-24 20:14:09.666339+00	\N	\N	\N	cli_scheduler	\N	airflow	{"host_name": "6b1fe676c3a8", "full_command": "['/home/airflow/.local/bin/airflow', 'scheduler']"}
5	2025-04-24 20:15:51.971547+00	\N	\N	\N	cli_users_create	\N	airflow	{"host_name": "056fbd958996", "full_command": "['/home/airflow/.local/bin/airflow', 'users', 'create', '--username', 'airflow', '--firstname', 'Airflow', '--lastname', 'Admin', '--role', 'Admin', '--email', 'airflow@airflow.com', '--password', '********']"}
6	2025-04-24 20:27:18.167804+00	\N	\N	\N	connection.create	\N	airflow	[]
7	2025-04-24 20:41:25.609818+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "6d50aafebeb6", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
8	2025-04-24 20:41:25.609942+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "fabfa9f5d3e1", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
9	2025-04-24 20:41:26.26225+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "b8e14a249a08", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
10	2025-04-24 20:41:26.308371+00	\N	\N	\N	cli_webserver	\N	airflow	{"host_name": "fabfa9f5d3e1", "full_command": "['/home/airflow/.local/bin/airflow', 'webserver']"}
11	2025-04-24 20:41:26.925003+00	\N	\N	\N	cli_upgradedb	\N	airflow	{"host_name": "b8e14a249a08", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'upgrade']"}
12	2025-04-24 20:41:27.6468+00	\N	\N	\N	cli_scheduler	\N	airflow	{"host_name": "6d50aafebeb6", "full_command": "['/home/airflow/.local/bin/airflow', 'scheduler']"}
13	2025-04-24 20:41:31.624065+00	\N	\N	\N	cli_users_create	\N	airflow	{"host_name": "b8e14a249a08", "full_command": "['/home/airflow/.local/bin/airflow', 'users', 'create', '--username', 'airflow', '--firstname', 'Airflow', '--lastname', 'Admin', '--email', 'airflowadmin@example.com', '--role', 'Admin', '--password', '********']"}
14	2025-04-24 20:44:30.476992+00	market_analysis_ingestion	\N	\N	trigger	\N	airflow	[('dag_id', 'market_analysis_ingestion'), ('unpause', 'True')]
15	2025-04-24 20:47:09.535331+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "8196a7f5786f", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
16	2025-04-24 20:47:09.535342+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "6ca8332e5db9", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
17	2025-04-24 20:47:10.045335+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "64a6ce8e73f3", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
18	2025-04-24 20:47:10.196625+00	\N	\N	\N	cli_webserver	\N	airflow	{"host_name": "8196a7f5786f", "full_command": "['/home/airflow/.local/bin/airflow', 'webserver']"}
19	2025-04-24 20:47:10.705629+00	\N	\N	\N	cli_upgradedb	\N	airflow	{"host_name": "64a6ce8e73f3", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'upgrade']"}
20	2025-04-24 20:47:11.472189+00	\N	\N	\N	cli_scheduler	\N	airflow	{"host_name": "6ca8332e5db9", "full_command": "['/home/airflow/.local/bin/airflow', 'scheduler']"}
21	2025-04-24 20:47:15.531686+00	\N	\N	\N	cli_users_create	\N	airflow	{"host_name": "64a6ce8e73f3", "full_command": "['/home/airflow/.local/bin/airflow', 'users', 'create', '--username', 'airflow', '--firstname', 'Airflow', '--lastname', 'Admin', '--email', 'airflowadmin@example.com', '--role', 'Admin', '--password', '********']"}
22	2025-04-24 20:47:27.747499+00	market_analysis_ingestion	\N	\N	grid	\N	airflow	[('dag_id', 'market_analysis_ingestion')]
23	2025-04-24 20:47:45.977613+00	market_analysis_ingestion	\N	\N	graph_data	\N	airflow	[('dag_id', 'market_analysis_ingestion')]
24	2025-04-24 20:55:51.366463+00	market_analysis_ingestion	\N	\N	grid	\N	airflow	[('dag_run_id', 'manual__2025-04-24T20:44:30.482568+00:00'), ('tab', 'graph'), ('dag_id', 'market_analysis_ingestion')]
25	2025-04-24 20:55:52.110724+00	market_analysis_ingestion	\N	\N	graph_data	\N	airflow	[('dag_id', 'market_analysis_ingestion')]
26	2025-04-25 12:46:43.502064+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "6ca8332e5db9", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
27	2025-04-25 12:46:43.503365+00	\N	\N	\N	cli_check	\N	airflow	{"host_name": "8196a7f5786f", "full_command": "['/home/airflow/.local/bin/airflow', 'db', 'check']"}
28	2025-04-25 12:46:44.54145+00	\N	\N	\N	cli_webserver	\N	airflow	{"host_name": "8196a7f5786f", "full_command": "['/home/airflow/.local/bin/airflow', 'webserver']"}
29	2025-04-25 12:46:46.679811+00	\N	\N	\N	cli_scheduler	\N	airflow	{"host_name": "6ca8332e5db9", "full_command": "['/home/airflow/.local/bin/airflow', 'scheduler']"}
\.


--
-- Data for Name: log_template; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.log_template (id, filename, elasticsearch_id, created_at) FROM stdin;
1	{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log	{dag_id}-{task_id}-{execution_date}-{try_number}	2025-04-24 20:13:23.251727+00
2	dag_id={{ ti.dag_id }}/run_id={{ ti.run_id }}/task_id={{ ti.task_id }}/{% if ti.map_index >= 0 %}map_index={{ ti.map_index }}/{% endif %}attempt={{ try_number }}.log	{dag_id}-{task_id}-{run_id}-{map_index}-{try_number}	2025-04-24 20:13:23.251736+00
\.


--
-- Data for Name: rendered_task_instance_fields; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.rendered_task_instance_fields (dag_id, task_id, run_id, map_index, rendered_fields, k8s_pod_yaml) FROM stdin;
\.


--
-- Data for Name: serialized_dag; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.serialized_dag (dag_id, fileloc, fileloc_hash, data, data_compressed, last_updated, dag_hash, processor_subdir) FROM stdin;
common_system_maintenance	/opt/airflow/dags/common/system_maintenance.py	43921834427787191	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/common/system_maintenance.py", "timetable": {"__type": "airflow.timetables.interval.CronDataIntervalTimetable", "__var": {"expression": "0 0 * * 0", "timezone": "UTC"}}, "timezone": "UTC", "edge_info": {}, "doc_md": "\\nSystem maintenance DAG.\\n\\nThis DAG performs system-wide maintenance tasks that affect all projects,\\nsuch as log cleanup, database optimization, and health checks.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "airflow_admin", "depends_on_past": false, "retries": 1, "retry_delay": {"__var": 300.0, "__type": "timedelta"}, "email_on_failure": true, "email": ["admin@example.com"]}, "__type": "dict"}, "tags": ["maintenance", "system", "common"], "_dag_id": "common_system_maintenance", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"cleanup_old_logs": ["operator", "cleanup_old_logs"], "optimize_airflow_db": ["operator", "optimize_airflow_db"], "check_disk_space": ["operator", "check_disk_space"], "check_connections": ["operator", "check_connections"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "_description": "System-wide maintenance tasks", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "default_pool", "owner": "airflow_admin", "task_id": "cleanup_old_logs", "template_fields": ["bash_command", "env"], "email": ["admin@example.com"], "_on_failure_fail_dagrun": false, "template_ext": [".sh", ".bash"], "retries": 1, "ui_color": "#f0ede4", "retry_delay": 300.0, "template_fields_renderers": {"bash_command": "bash", "env": "json"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["optimize_airflow_db"], "_task_type": "BashOperator", "_task_module": "airflow.operators.bash", "_is_empty": false, "bash_command": "find /opt/airflow/logs -type f -name \\"*.log\\" -mtime +30 -delete"}, {"_is_teardown": false, "pool": "default_pool", "owner": "airflow_admin", "task_id": "optimize_airflow_db", "template_fields": ["bash_command", "env"], "email": ["admin@example.com"], "_on_failure_fail_dagrun": false, "template_ext": [".sh", ".bash"], "retries": 1, "ui_color": "#f0ede4", "retry_delay": 300.0, "template_fields_renderers": {"bash_command": "bash", "env": "json"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "BashOperator", "_task_module": "airflow.operators.bash", "_is_empty": false, "bash_command": "airflow db clean --clean-before-timestamp \\"$(date -d \\"-30 days\\" \\"+%Y-%m-%d\\")\\""}, {"_is_teardown": false, "pool": "default_pool", "owner": "airflow_admin", "task_id": "check_disk_space", "template_fields": ["templates_dict", "op_args", "op_kwargs"], "email": ["admin@example.com"], "_on_failure_fail_dagrun": false, "template_ext": [], "retries": 1, "ui_color": "#ffefeb", "retry_delay": 300.0, "template_fields_renderers": {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["check_connections"], "_task_type": "PythonOperator", "_task_module": "airflow.operators.python", "_is_empty": false, "op_args": [], "op_kwargs": {}}, {"_is_teardown": false, "pool": "default_pool", "owner": "airflow_admin", "task_id": "check_connections", "template_fields": ["templates_dict", "op_args", "op_kwargs"], "email": ["admin@example.com"], "_on_failure_fail_dagrun": false, "template_ext": [], "retries": 1, "ui_color": "#ffefeb", "retry_delay": 300.0, "template_fields_renderers": {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "PythonOperator", "_task_module": "airflow.operators.python", "_is_empty": false, "op_args": [], "op_kwargs": {}}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.759254+00	34595422ad3b5b9715a220bee88d1a94	\N
market_analysis_ingestion	/opt/airflow/dags/market-analysis/dag_market_analysis_ingestion.py	6932960973159084	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/market-analysis/dag_market_analysis_ingestion.py", "timezone": "UTC", "edge_info": {}, "doc_md": "\\nMarket Analysis Ingestion DAG.\\n\\nThis DAG uses the `market-analysis:latest` Docker image to fetch daily market data\\nfor a specified symbol and date using the market-analysis script.\\n\\nIt requires the Airflow Variables `binance_api_key` and `binance_secret_key` to be set,\\nwhich contain the necessary credentials for the Binance API. These variables are\\npassed as environment variables to the Docker container run by the `DockerOperator`.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "analytics_team", "depends_on_past": false, "retries": 2, "retry_delay": {"__var": 300.0, "__type": "timedelta"}, "pool": "project_market_analysis_pool"}, "__type": "dict"}, "tags": ["market-analysis", "ingestion"], "_dag_id": "market_analysis_ingestion", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"ingest_market_data": ["operator", "ingest_market_data"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "schedule_interval": "@daily", "_description": "Ingest market data via market-analysis container", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "project_market_analysis_pool", "owner": "analytics_team", "task_id": "ingest_market_data", "template_fields": ["image", "command", "environment", "env_file", "container_name"], "_on_failure_fail_dagrun": false, "params": {"symbol": {"__class": "airflow.models.param.Param", "default": "AAPL", "description": null, "schema": {"__var": {}, "__type": "dict"}}}, "template_ext": [".sh", ".bash", ".env"], "retries": 2, "execution_timeout": 1800.0, "ui_color": "#fff", "retry_delay": 300.0, "template_fields_renderers": {"env_file": "yaml"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "DockerOperator", "_task_module": "airflow.providers.docker.operators.docker", "_is_empty": false, "image": "market-analysis:latest", "command": ["python", "-m", "src.main", "--symbol", "{{ params.symbol }}", "--start", "{{ ds }}", "--end", "{{ ds }}"], "environment": {"BINANCE_API_KEY": "{{ var.value.binance_api_key }}", "BINANCE_SECRET_KEY": "{{ var.value.binance_secret_key }}"}}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.246884+00	626d9716205f99f36ab9ed93cee8c7ed	\N
project_trading_daily_sync	/opt/airflow/dags/project_trading/trading_daily_sync.py	48767742691821281	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/project_trading/trading_daily_sync.py", "timetable": {"__type": "airflow.timetables.interval.CronDataIntervalTimetable", "__var": {"expression": "0 1 * * *", "timezone": "UTC"}}, "timezone": "UTC", "edge_info": {}, "doc_md": "\\nDaily trading data synchronization DAG.\\n\\nThis DAG extracts trading data from Interactive Brokers, processes it,\\nand loads it into a data warehouse for analysis.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "trading_team", "depends_on_past": false, "retries": 3, "retry_delay": 300, "pool": "project_trading_pool"}, "__type": "dict"}, "tags": ["trading", "ibkr"], "_dag_id": "project_trading_daily_sync", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"extract_ibkr_data": ["operator", "extract_ibkr_data"], "process_trading_data": ["operator", "process_trading_data"], "load_processed_data": ["operator", "load_processed_data"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "_description": "Syncs daily trading data from IBKR to data warehouse", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "project_trading_pool", "owner": "trading_team", "task_id": "extract_ibkr_data", "template_fields": ["image", "command", "environment", "env_file", "container_name"], "_on_failure_fail_dagrun": false, "template_ext": [".sh", ".bash", ".env"], "retries": 3, "ui_color": "#fff", "retry_delay": 300.0, "template_fields_renderers": {"env_file": "yaml"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["process_trading_data"], "_task_type": "DockerOperator", "_task_module": "airflow.providers.docker.operators.docker", "_is_empty": false, "image": "project_trading:latest", "command": ["python", "/app/plugins/project_trading/extract_ibkr_data.py", "--conn-id", "project_trading_ibkr", "--data-types", "trades", "positions", "market_data", "--start-date", "{{ ds }}", "--end-date", "{{ ds }}", "--output-path", "/tmp/data/{{ ds }}"], "environment": {}}, {"_is_teardown": false, "pool": "project_trading_pool", "owner": "trading_team", "task_id": "process_trading_data", "template_fields": ["image", "command", "environment", "env_file", "container_name"], "_on_failure_fail_dagrun": false, "template_ext": [".sh", ".bash", ".env"], "retries": 3, "ui_color": "#fff", "retry_delay": 300.0, "template_fields_renderers": {"env_file": "yaml"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["load_processed_data"], "_task_type": "DockerOperator", "_task_module": "airflow.providers.docker.operators.docker", "_is_empty": false, "image": "trading-project:latest", "command": "python /scripts/process_trading_data.py", "environment": {"DATA_DATE": "{{ ds }}", "DATA_PATH": "/tmp/data/{{ ds }}"}}, {"_is_teardown": false, "pool": "project_trading_pool", "owner": "trading_team", "task_id": "load_processed_data", "template_fields": ["sql"], "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 3, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "CALL trading.load_daily_data('{{ ds }}')"}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.53363+00	3142d6a94f47a9268def54883221d2b8	\N
project_analytics_client1_reporting	/opt/airflow/dags/project_analytics/client_reporting_factory.py	61179450594028497	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/project_analytics/client_reporting_factory.py", "timetable": {"__type": "airflow.timetables.interval.CronDataIntervalTimetable", "__var": {"expression": "0 6 * * *", "timezone": "UTC"}}, "timezone": "UTC", "edge_info": {}, "doc_md": "\\nClient reporting DAG factory.\\n\\nThis module demonstrates the DAG factory pattern for generating multiple similar DAGs,\\none for each client's reporting needs. This approach avoids code duplication while\\nmaintaining clear separation between client-specific workflows.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "analytics_team", "depends_on_past": false, "retries": 2, "retry_delay": {"__var": 300.0, "__type": "timedelta"}, "pool": "project_analytics_pool", "email_on_failure": true, "email_on_retry": false, "email": ["client1@example.com"]}, "__type": "dict"}, "tags": ["analytics", "reporting", "client1"], "_dag_id": "project_analytics_client1_reporting", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"generate_client_reports": ["operator", "generate_client_reports"], "export_reports_to_storage": ["operator", "export_reports_to_storage"], "send_email_notification": ["operator", "send_email_notification"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "_description": "Daily reporting for client1", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "generate_client_reports", "template_fields": ["sql"], "email": ["client1@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["export_reports_to_storage"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Generate client-specific reports\\n        CALL analytics.generate_client_reports(\\n            'client1',\\n            '{{ ds }}',\\n            'summary,detailed,forecast'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "export_reports_to_storage", "template_fields": ["sql"], "email": ["client1@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["send_email_notification"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Export reports to cloud storage\\n        CALL analytics.export_client_reports_to_storage(\\n            'client1',\\n            '{{ ds }}'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "send_email_notification", "template_fields": ["templates_dict", "op_args", "op_kwargs"], "email": ["client1@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [], "retries": 2, "ui_color": "#ffefeb", "retry_delay": 300.0, "template_fields_renderers": {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "PythonOperator", "_task_module": "airflow.operators.python", "_is_empty": false, "op_args": [], "op_kwargs": {"client_id": "client1", "report_date": "{{ ds }}", "report_types": ["summary", "detailed", "forecast"], "recipient_email": "client1@example.com"}}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.665653+00	7b5d3d958e12452a052609c62dc52b3d	\N
project_analytics_client2_reporting	/opt/airflow/dags/project_analytics/client_reporting_factory.py	61179450594028497	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/project_analytics/client_reporting_factory.py", "timetable": {"__type": "airflow.timetables.interval.CronDataIntervalTimetable", "__var": {"expression": "0 7 * * *", "timezone": "UTC"}}, "timezone": "UTC", "edge_info": {}, "doc_md": "\\nClient reporting DAG factory.\\n\\nThis module demonstrates the DAG factory pattern for generating multiple similar DAGs,\\none for each client's reporting needs. This approach avoids code duplication while\\nmaintaining clear separation between client-specific workflows.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "analytics_team", "depends_on_past": false, "retries": 2, "retry_delay": {"__var": 300.0, "__type": "timedelta"}, "pool": "project_analytics_pool", "email_on_failure": true, "email_on_retry": false, "email": ["client2@example.com"]}, "__type": "dict"}, "tags": ["analytics", "reporting", "client2"], "_dag_id": "project_analytics_client2_reporting", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"generate_client_reports": ["operator", "generate_client_reports"], "export_reports_to_storage": ["operator", "export_reports_to_storage"], "send_email_notification": ["operator", "send_email_notification"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "_description": "Daily reporting for client2", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "generate_client_reports", "template_fields": ["sql"], "email": ["client2@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["export_reports_to_storage"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Generate client-specific reports\\n        CALL analytics.generate_client_reports(\\n            'client2',\\n            '{{ ds }}',\\n            'summary,detailed'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "export_reports_to_storage", "template_fields": ["sql"], "email": ["client2@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["send_email_notification"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Export reports to cloud storage\\n        CALL analytics.export_client_reports_to_storage(\\n            'client2',\\n            '{{ ds }}'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "send_email_notification", "template_fields": ["templates_dict", "op_args", "op_kwargs"], "email": ["client2@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [], "retries": 2, "ui_color": "#ffefeb", "retry_delay": 300.0, "template_fields_renderers": {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "PythonOperator", "_task_module": "airflow.operators.python", "_is_empty": false, "op_args": [], "op_kwargs": {"client_id": "client2", "report_date": "{{ ds }}", "report_types": ["summary", "detailed"], "recipient_email": "client2@example.com"}}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.713891+00	21c3619be963525ab8246d5c869f275f	\N
project_analytics_client3_reporting	/opt/airflow/dags/project_analytics/client_reporting_factory.py	61179450594028497	{"__version": 1, "dag": {"start_date": 1745452800.0, "fileloc": "/opt/airflow/dags/project_analytics/client_reporting_factory.py", "timetable": {"__type": "airflow.timetables.interval.CronDataIntervalTimetable", "__var": {"expression": "0 8 * * 1-5", "timezone": "UTC"}}, "timezone": "UTC", "edge_info": {}, "doc_md": "\\nClient reporting DAG factory.\\n\\nThis module demonstrates the DAG factory pattern for generating multiple similar DAGs,\\none for each client's reporting needs. This approach avoids code duplication while\\nmaintaining clear separation between client-specific workflows.\\n", "dataset_triggers": [], "default_args": {"__var": {"owner": "analytics_team", "depends_on_past": false, "retries": 2, "retry_delay": {"__var": 300.0, "__type": "timedelta"}, "pool": "project_analytics_pool", "email_on_failure": true, "email_on_retry": false, "email": ["client3@example.com"]}, "__type": "dict"}, "tags": ["analytics", "reporting", "client3"], "_dag_id": "project_analytics_client3_reporting", "_task_group": {"_group_id": null, "prefix_group_id": true, "tooltip": "", "ui_color": "CornflowerBlue", "ui_fgcolor": "#000", "children": {"generate_client_reports": ["operator", "generate_client_reports"], "export_reports_to_storage": ["operator", "export_reports_to_storage"], "send_email_notification": ["operator", "send_email_notification"]}, "upstream_group_ids": [], "downstream_group_ids": [], "upstream_task_ids": [], "downstream_task_ids": []}, "_description": "Daily reporting for client3", "_processor_dags_folder": "/opt/airflow/dags", "tasks": [{"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "generate_client_reports", "template_fields": ["sql"], "email": ["client3@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["export_reports_to_storage"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Generate client-specific reports\\n        CALL analytics.generate_client_reports(\\n            'client3',\\n            '{{ ds }}',\\n            'summary'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "export_reports_to_storage", "template_fields": ["sql"], "email": ["client3@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [".sql"], "retries": 2, "ui_color": "#ededed", "retry_delay": 300.0, "template_fields_renderers": {"sql": "sql"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": ["send_email_notification"], "_task_type": "SnowflakeOperator", "_task_module": "airflow.providers.snowflake.operators.snowflake", "_is_empty": false, "sql": "\\n        -- Export reports to cloud storage\\n        CALL analytics.export_client_reports_to_storage(\\n            'client3',\\n            '{{ ds }}'\\n        );\\n        "}, {"_is_teardown": false, "pool": "project_analytics_pool", "owner": "analytics_team", "task_id": "send_email_notification", "template_fields": ["templates_dict", "op_args", "op_kwargs"], "email": ["client3@example.com"], "email_on_retry": false, "_on_failure_fail_dagrun": false, "template_ext": [], "retries": 2, "ui_color": "#ffefeb", "retry_delay": 300.0, "template_fields_renderers": {"templates_dict": "json", "op_args": "py", "op_kwargs": "py"}, "_is_setup": false, "ui_fgcolor": "#000", "downstream_task_ids": [], "_task_type": "PythonOperator", "_task_module": "airflow.operators.python", "_is_empty": false, "op_args": [], "op_kwargs": {"client_id": "client3", "report_date": "{{ ds }}", "report_types": ["summary"], "recipient_email": "client3@example.com"}}], "dag_dependencies": [], "params": {}}}	\N	2025-04-25 12:46:54.724539+00	9946c978b9873ffdb2cc1aa19439a2f4	\N
\.


--
-- Data for Name: session; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.session (id, session_id, data, expiry) FROM stdin;
3	9213aa1c-7b3b-4a35-b42b-b6867abfac51	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710288580a000000637372665f746f6b656e7103582800000063616436623235616434323131383330633038393033353061343062646265393533333032663534710458060000006c6f63616c6571055802000000656e710658080000005f757365725f696471074b0158030000005f6964710858800000006563323564666138313630613831356636343634326564353232363465326334386364303238383263626464303564653937326434633163343263613530623735666332306137316430353164323137343563626134646663613164643766383662623438393936363464663466363565663330306262396632313865393665710958110000006461675f7374617475735f66696c746572710a5803000000616c6c710b580c000000706167655f686973746f7279710c5d710d285826000000687474703a2f2f6c6f63616c686f73743a383038302f636f6e6e656374696f6e2f6c6973742f710e5824000000687474703a2f2f6c6f63616c686f73743a383038302f636f6e6e656374696f6e2f616464710f65752e	2025-05-24 20:31:24.261157
1	4be32bb4-75e4-4153-abda-252507b7699a	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710289580a000000637372665f746f6b656e7103582800000063616436623235616434323131383330633038393033353061343062646265393533333032663534710458060000006c6f63616c6571055802000000656e7106752e	2025-05-24 20:16:30.744895
2	a2c750fd-28f9-436b-ba43-3b3e4567ac16	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710289580a000000637372665f746f6b656e7103582800000035623337666264646630636463376331383739366237306662643065323436653433633635366564710458060000006c6f63616c6571055802000000656e7106752e	2025-05-24 20:14:18.013211
4	309b5b65-9434-4414-a036-392ee8cdd1b4	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710289580a000000637372665f746f6b656e7103582800000062613537643065646136646464636666663864376134656132613566373965313235346537626566710458060000006c6f63616c6571055802000000656e7106752e	2025-05-24 20:42:45.786287
7	82200f9f-a943-49e8-b818-56706c129301	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710288580a000000637372665f746f6b656e7103582800000065396331643138613765306439326130643231373463373535323233363131653733363237653866710458060000006c6f63616c6571055802000000656e710658080000005f757365725f696471074b0158030000005f6964710858800000006563323564666138313630613831356636343634326564353232363465326334386364303238383263626464303564653937326434633163343263613530623735666332306137316430353164323137343563626134646663613164643766383662623438393936363464663466363565663330306262396632313865393665710958110000006461675f7374617475735f66696c746572710a5803000000616c6c710b752e	2025-05-24 21:00:54.309258
5	2d3e78d0-7d10-4695-b83f-28794f3811f7	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710288580a000000637372665f746f6b656e7103582800000062613537643065646136646464636666663864376134656132613566373965313235346537626566710458060000006c6f63616c6571055802000000656e710658080000005f757365725f696471074b0158030000005f6964710858800000006563323564666138313630613831356636343634326564353232363465326334386364303238383263626464303564653937326434633163343263613530623735666332306137316430353164323137343563626134646663613164643766383662623438393936363464663466363565663330306262396632313865393665710958110000006461675f7374617475735f66696c746572710a5803000000616c6c710b752e	2025-05-24 20:46:49.130657
6	cef630bc-1571-438c-9f0b-13eb98b2627b	\\x80037d710028580a0000005f7065726d616e656e7471018858060000005f6672657368710289580a000000637372665f746f6b656e7103582800000065396331643138613765306439326130643231373463373535323233363131653733363237653866710458060000006c6f63616c6571055802000000656e7106752e	2025-05-24 20:47:23.54813
\.


--
-- Data for Name: sla_miss; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.sla_miss (task_id, dag_id, execution_date, email_sent, "timestamp", description, notification_sent) FROM stdin;
\.


--
-- Data for Name: slot_pool; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.slot_pool (id, pool, slots, description) FROM stdin;
1	default_pool	128	Default pool
\.


--
-- Data for Name: task_fail; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_fail (id, task_id, dag_id, run_id, map_index, start_date, end_date, duration) FROM stdin;
\.


--
-- Data for Name: task_instance; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_instance (task_id, dag_id, run_id, map_index, start_date, end_date, duration, state, try_number, max_tries, hostname, unixname, job_id, pool, pool_slots, queue, priority_weight, operator, queued_dttm, queued_by_job_id, pid, executor_config, updated_at, external_executor_id, trigger_id, trigger_timeout, next_method, next_kwargs) FROM stdin;
ingest_market_data	market_analysis_ingestion	scheduled__2025-04-23T00:00:00+00:00	-1	\N	\N	\N	scheduled	0	2		airflow	\N	project_market_analysis_pool	1	default	1	DockerOperator	\N	\N	\N	\\x80047d942e	2025-04-24 20:44:31.002875+00	\N	\N	\N	\N	\N
ingest_market_data	market_analysis_ingestion	manual__2025-04-24T20:44:30.482568+00:00	-1	\N	\N	\N	scheduled	0	2		airflow	\N	project_market_analysis_pool	1	default	1	DockerOperator	\N	\N	\N	\\x80047d942e	2025-04-24 20:44:31.008367+00	\N	\N	\N	\N	\N
ingest_market_data	market_analysis_ingestion	scheduled__2025-04-24T00:00:00+00:00	-1	\N	\N	\N	scheduled	0	2		airflow	\N	project_market_analysis_pool	1	default	1	DockerOperator	\N	\N	\N	\\x80047d942e	2025-04-25 12:46:53.794053+00	\N	\N	\N	\N	\N
\.


--
-- Data for Name: task_instance_note; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_instance_note (user_id, task_id, dag_id, run_id, map_index, content, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_map; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_map (dag_id, task_id, run_id, map_index, length, keys) FROM stdin;
\.


--
-- Data for Name: task_outlet_dataset_reference; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_outlet_dataset_reference (dataset_id, dag_id, task_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_reschedule; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.task_reschedule (id, task_id, dag_id, run_id, map_index, try_number, start_date, end_date, duration, reschedule_date) FROM stdin;
\.


--
-- Data for Name: trigger; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.trigger (id, classpath, kwargs, created_date, triggerer_id) FROM stdin;
\.


--
-- Data for Name: variable; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.variable (id, key, val, description, is_encrypted) FROM stdin;
\.


--
-- Data for Name: xcom; Type: TABLE DATA; Schema: public; Owner: airflow
--

COPY public.xcom (dag_run_id, task_id, map_index, key, dag_id, run_id, value, "timestamp") FROM stdin;
\.


--
-- Name: ab_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_permission_id_seq', 10, true);


--
-- Name: ab_permission_view_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_permission_view_id_seq', 110, true);


--
-- Name: ab_permission_view_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_permission_view_role_id_seq', 222, true);


--
-- Name: ab_register_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_register_user_id_seq', 1, false);


--
-- Name: ab_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_role_id_seq', 5, true);


--
-- Name: ab_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_user_id_seq', 1, true);


--
-- Name: ab_user_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_user_role_id_seq', 1, true);


--
-- Name: ab_view_menu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.ab_view_menu_id_seq', 56, true);


--
-- Name: callback_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.callback_request_id_seq', 1, false);


--
-- Name: connection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.connection_id_seq', 57, true);


--
-- Name: dag_pickle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.dag_pickle_id_seq', 1, false);


--
-- Name: dag_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.dag_run_id_seq', 3, true);


--
-- Name: dataset_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.dataset_event_id_seq', 1, false);


--
-- Name: dataset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.dataset_id_seq', 1, false);


--
-- Name: import_error_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.import_error_id_seq', 1, true);


--
-- Name: job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.job_id_seq', 4, true);


--
-- Name: log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.log_id_seq', 29, true);


--
-- Name: log_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.log_template_id_seq', 2, true);


--
-- Name: session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.session_id_seq', 7, true);


--
-- Name: slot_pool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.slot_pool_id_seq', 1, true);


--
-- Name: task_fail_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.task_fail_id_seq', 1, false);


--
-- Name: task_reschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.task_reschedule_id_seq', 1, false);


--
-- Name: trigger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.trigger_id_seq', 1, false);


--
-- Name: variable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: airflow
--

SELECT pg_catalog.setval('public.variable_id_seq', 1, false);


--
-- Name: ab_permission ab_permission_name_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission
    ADD CONSTRAINT ab_permission_name_uq UNIQUE (name);


--
-- Name: ab_permission ab_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission
    ADD CONSTRAINT ab_permission_pkey PRIMARY KEY (id);


--
-- Name: ab_permission_view ab_permission_view_permission_id_view_menu_id_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view
    ADD CONSTRAINT ab_permission_view_permission_id_view_menu_id_uq UNIQUE (permission_id, view_menu_id);


--
-- Name: ab_permission_view ab_permission_view_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view
    ADD CONSTRAINT ab_permission_view_pkey PRIMARY KEY (id);


--
-- Name: ab_permission_view_role ab_permission_view_role_permission_view_id_role_id_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view_role
    ADD CONSTRAINT ab_permission_view_role_permission_view_id_role_id_uq UNIQUE (permission_view_id, role_id);


--
-- Name: ab_permission_view_role ab_permission_view_role_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view_role
    ADD CONSTRAINT ab_permission_view_role_pkey PRIMARY KEY (id);


--
-- Name: ab_register_user ab_register_user_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_register_user
    ADD CONSTRAINT ab_register_user_pkey PRIMARY KEY (id);


--
-- Name: ab_register_user ab_register_user_username_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_register_user
    ADD CONSTRAINT ab_register_user_username_uq UNIQUE (username);


--
-- Name: ab_role ab_role_name_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_role
    ADD CONSTRAINT ab_role_name_uq UNIQUE (name);


--
-- Name: ab_role ab_role_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_role
    ADD CONSTRAINT ab_role_pkey PRIMARY KEY (id);


--
-- Name: ab_user ab_user_email_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user
    ADD CONSTRAINT ab_user_email_uq UNIQUE (email);


--
-- Name: ab_user ab_user_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user
    ADD CONSTRAINT ab_user_pkey PRIMARY KEY (id);


--
-- Name: ab_user_role ab_user_role_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user_role
    ADD CONSTRAINT ab_user_role_pkey PRIMARY KEY (id);


--
-- Name: ab_user_role ab_user_role_user_id_role_id_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user_role
    ADD CONSTRAINT ab_user_role_user_id_role_id_uq UNIQUE (user_id, role_id);


--
-- Name: ab_user ab_user_username_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user
    ADD CONSTRAINT ab_user_username_uq UNIQUE (username);


--
-- Name: ab_view_menu ab_view_menu_name_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_view_menu
    ADD CONSTRAINT ab_view_menu_name_uq UNIQUE (name);


--
-- Name: ab_view_menu ab_view_menu_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_view_menu
    ADD CONSTRAINT ab_view_menu_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: callback_request callback_request_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.callback_request
    ADD CONSTRAINT callback_request_pkey PRIMARY KEY (id);


--
-- Name: connection connection_conn_id_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.connection
    ADD CONSTRAINT connection_conn_id_uq UNIQUE (conn_id);


--
-- Name: connection connection_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.connection
    ADD CONSTRAINT connection_pkey PRIMARY KEY (id);


--
-- Name: dag_code dag_code_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_code
    ADD CONSTRAINT dag_code_pkey PRIMARY KEY (fileloc_hash);


--
-- Name: dag_owner_attributes dag_owner_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_owner_attributes
    ADD CONSTRAINT dag_owner_attributes_pkey PRIMARY KEY (dag_id, owner);


--
-- Name: dag_pickle dag_pickle_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_pickle
    ADD CONSTRAINT dag_pickle_pkey PRIMARY KEY (id);


--
-- Name: dag dag_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag
    ADD CONSTRAINT dag_pkey PRIMARY KEY (dag_id);


--
-- Name: dag_run dag_run_dag_id_execution_date_key; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run
    ADD CONSTRAINT dag_run_dag_id_execution_date_key UNIQUE (dag_id, execution_date);


--
-- Name: dag_run dag_run_dag_id_run_id_key; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run
    ADD CONSTRAINT dag_run_dag_id_run_id_key UNIQUE (dag_id, run_id);


--
-- Name: dag_run_note dag_run_note_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run_note
    ADD CONSTRAINT dag_run_note_pkey PRIMARY KEY (dag_run_id);


--
-- Name: dag_run dag_run_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run
    ADD CONSTRAINT dag_run_pkey PRIMARY KEY (id);


--
-- Name: dag_tag dag_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_tag
    ADD CONSTRAINT dag_tag_pkey PRIMARY KEY (name, dag_id);


--
-- Name: dag_warning dag_warning_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_warning
    ADD CONSTRAINT dag_warning_pkey PRIMARY KEY (dag_id, warning_type);


--
-- Name: dagrun_dataset_event dagrun_dataset_event_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dagrun_dataset_event
    ADD CONSTRAINT dagrun_dataset_event_pkey PRIMARY KEY (dag_run_id, event_id);


--
-- Name: dataset_event dataset_event_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset_event
    ADD CONSTRAINT dataset_event_pkey PRIMARY KEY (id);


--
-- Name: dataset dataset_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset
    ADD CONSTRAINT dataset_pkey PRIMARY KEY (id);


--
-- Name: dataset_dag_run_queue datasetdagrunqueue_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset_dag_run_queue
    ADD CONSTRAINT datasetdagrunqueue_pkey PRIMARY KEY (dataset_id, target_dag_id);


--
-- Name: dag_schedule_dataset_reference dsdr_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_schedule_dataset_reference
    ADD CONSTRAINT dsdr_pkey PRIMARY KEY (dataset_id, dag_id);


--
-- Name: import_error import_error_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.import_error
    ADD CONSTRAINT import_error_pkey PRIMARY KEY (id);


--
-- Name: job job_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.job
    ADD CONSTRAINT job_pkey PRIMARY KEY (id);


--
-- Name: log log_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.log
    ADD CONSTRAINT log_pkey PRIMARY KEY (id);


--
-- Name: log_template log_template_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.log_template
    ADD CONSTRAINT log_template_pkey PRIMARY KEY (id);


--
-- Name: rendered_task_instance_fields rendered_task_instance_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.rendered_task_instance_fields
    ADD CONSTRAINT rendered_task_instance_fields_pkey PRIMARY KEY (dag_id, task_id, run_id, map_index);


--
-- Name: serialized_dag serialized_dag_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.serialized_dag
    ADD CONSTRAINT serialized_dag_pkey PRIMARY KEY (dag_id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: session session_session_id_key; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_session_id_key UNIQUE (session_id);


--
-- Name: sla_miss sla_miss_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.sla_miss
    ADD CONSTRAINT sla_miss_pkey PRIMARY KEY (task_id, dag_id, execution_date);


--
-- Name: slot_pool slot_pool_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.slot_pool
    ADD CONSTRAINT slot_pool_pkey PRIMARY KEY (id);


--
-- Name: slot_pool slot_pool_pool_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.slot_pool
    ADD CONSTRAINT slot_pool_pool_uq UNIQUE (pool);


--
-- Name: task_fail task_fail_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_fail
    ADD CONSTRAINT task_fail_pkey PRIMARY KEY (id);


--
-- Name: task_instance_note task_instance_note_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance_note
    ADD CONSTRAINT task_instance_note_pkey PRIMARY KEY (task_id, dag_id, run_id, map_index);


--
-- Name: task_instance task_instance_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance
    ADD CONSTRAINT task_instance_pkey PRIMARY KEY (dag_id, task_id, run_id, map_index);


--
-- Name: task_map task_map_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_map
    ADD CONSTRAINT task_map_pkey PRIMARY KEY (dag_id, task_id, run_id, map_index);


--
-- Name: task_reschedule task_reschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_reschedule
    ADD CONSTRAINT task_reschedule_pkey PRIMARY KEY (id);


--
-- Name: task_outlet_dataset_reference todr_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_outlet_dataset_reference
    ADD CONSTRAINT todr_pkey PRIMARY KEY (dataset_id, dag_id, task_id);


--
-- Name: trigger trigger_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.trigger
    ADD CONSTRAINT trigger_pkey PRIMARY KEY (id);


--
-- Name: variable variable_key_uq; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.variable
    ADD CONSTRAINT variable_key_uq UNIQUE (key);


--
-- Name: variable variable_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.variable
    ADD CONSTRAINT variable_pkey PRIMARY KEY (id);


--
-- Name: xcom xcom_pkey; Type: CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.xcom
    ADD CONSTRAINT xcom_pkey PRIMARY KEY (dag_run_id, task_id, map_index, key);


--
-- Name: dag_id_state; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX dag_id_state ON public.dag_run USING btree (dag_id, state);


--
-- Name: idx_ab_register_user_username; Type: INDEX; Schema: public; Owner: airflow
--

CREATE UNIQUE INDEX idx_ab_register_user_username ON public.ab_register_user USING btree (lower((username)::text));


--
-- Name: idx_ab_user_username; Type: INDEX; Schema: public; Owner: airflow
--

CREATE UNIQUE INDEX idx_ab_user_username ON public.ab_user USING btree (lower((username)::text));


--
-- Name: idx_dag_run_dag_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dag_run_dag_id ON public.dag_run USING btree (dag_id);


--
-- Name: idx_dag_run_queued_dags; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dag_run_queued_dags ON public.dag_run USING btree (state, dag_id) WHERE ((state)::text = 'queued'::text);


--
-- Name: idx_dag_run_running_dags; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dag_run_running_dags ON public.dag_run USING btree (state, dag_id) WHERE ((state)::text = 'running'::text);


--
-- Name: idx_dagrun_dataset_events_dag_run_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dagrun_dataset_events_dag_run_id ON public.dagrun_dataset_event USING btree (dag_run_id);


--
-- Name: idx_dagrun_dataset_events_event_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dagrun_dataset_events_event_id ON public.dagrun_dataset_event USING btree (event_id);


--
-- Name: idx_dataset_id_timestamp; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_dataset_id_timestamp ON public.dataset_event USING btree (dataset_id, "timestamp");


--
-- Name: idx_fileloc_hash; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_fileloc_hash ON public.serialized_dag USING btree (fileloc_hash);


--
-- Name: idx_job_dag_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_job_dag_id ON public.job USING btree (dag_id);


--
-- Name: idx_job_state_heartbeat; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_job_state_heartbeat ON public.job USING btree (state, latest_heartbeat);


--
-- Name: idx_last_scheduling_decision; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_last_scheduling_decision ON public.dag_run USING btree (last_scheduling_decision);


--
-- Name: idx_log_dag; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_log_dag ON public.log USING btree (dag_id);


--
-- Name: idx_log_dttm; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_log_dttm ON public.log USING btree (dttm);


--
-- Name: idx_log_event; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_log_event ON public.log USING btree (event);


--
-- Name: idx_next_dagrun_create_after; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_next_dagrun_create_after ON public.dag USING btree (next_dagrun_create_after);


--
-- Name: idx_root_dag_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_root_dag_id ON public.dag USING btree (root_dag_id);


--
-- Name: idx_task_fail_task_instance; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_task_fail_task_instance ON public.task_fail USING btree (dag_id, task_id, run_id, map_index);


--
-- Name: idx_task_reschedule_dag_run; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_task_reschedule_dag_run ON public.task_reschedule USING btree (dag_id, run_id);


--
-- Name: idx_task_reschedule_dag_task_run; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_task_reschedule_dag_task_run ON public.task_reschedule USING btree (dag_id, task_id, run_id, map_index);


--
-- Name: idx_uri_unique; Type: INDEX; Schema: public; Owner: airflow
--

CREATE UNIQUE INDEX idx_uri_unique ON public.dataset USING btree (uri);


--
-- Name: idx_xcom_key; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_xcom_key ON public.xcom USING btree (key);


--
-- Name: idx_xcom_task_instance; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX idx_xcom_task_instance ON public.xcom USING btree (dag_id, task_id, run_id, map_index);


--
-- Name: job_type_heart; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX job_type_heart ON public.job USING btree (job_type, latest_heartbeat);


--
-- Name: sm_dag; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX sm_dag ON public.sla_miss USING btree (dag_id);


--
-- Name: ti_dag_run; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_dag_run ON public.task_instance USING btree (dag_id, run_id);


--
-- Name: ti_dag_state; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_dag_state ON public.task_instance USING btree (dag_id, state);


--
-- Name: ti_job_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_job_id ON public.task_instance USING btree (job_id);


--
-- Name: ti_pool; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_pool ON public.task_instance USING btree (pool, state, priority_weight);


--
-- Name: ti_state; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_state ON public.task_instance USING btree (state);


--
-- Name: ti_state_lkp; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_state_lkp ON public.task_instance USING btree (dag_id, task_id, run_id, state);


--
-- Name: ti_trigger_id; Type: INDEX; Schema: public; Owner: airflow
--

CREATE INDEX ti_trigger_id ON public.task_instance USING btree (trigger_id);


--
-- Name: ab_permission_view ab_permission_view_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view
    ADD CONSTRAINT ab_permission_view_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.ab_permission(id);


--
-- Name: ab_permission_view_role ab_permission_view_role_permission_view_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view_role
    ADD CONSTRAINT ab_permission_view_role_permission_view_id_fkey FOREIGN KEY (permission_view_id) REFERENCES public.ab_permission_view(id);


--
-- Name: ab_permission_view_role ab_permission_view_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view_role
    ADD CONSTRAINT ab_permission_view_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.ab_role(id);


--
-- Name: ab_permission_view ab_permission_view_view_menu_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_permission_view
    ADD CONSTRAINT ab_permission_view_view_menu_id_fkey FOREIGN KEY (view_menu_id) REFERENCES public.ab_view_menu(id);


--
-- Name: ab_user ab_user_changed_by_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user
    ADD CONSTRAINT ab_user_changed_by_fk_fkey FOREIGN KEY (changed_by_fk) REFERENCES public.ab_user(id);


--
-- Name: ab_user ab_user_created_by_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user
    ADD CONSTRAINT ab_user_created_by_fk_fkey FOREIGN KEY (created_by_fk) REFERENCES public.ab_user(id);


--
-- Name: ab_user_role ab_user_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user_role
    ADD CONSTRAINT ab_user_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.ab_role(id);


--
-- Name: ab_user_role ab_user_role_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.ab_user_role
    ADD CONSTRAINT ab_user_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.ab_user(id);


--
-- Name: dag_owner_attributes dag.dag_id; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_owner_attributes
    ADD CONSTRAINT "dag.dag_id" FOREIGN KEY (dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: dag_run_note dag_run_note_dr_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run_note
    ADD CONSTRAINT dag_run_note_dr_fkey FOREIGN KEY (dag_run_id) REFERENCES public.dag_run(id) ON DELETE CASCADE;


--
-- Name: dag_run_note dag_run_note_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run_note
    ADD CONSTRAINT dag_run_note_user_fkey FOREIGN KEY (user_id) REFERENCES public.ab_user(id);


--
-- Name: dag_tag dag_tag_dag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_tag
    ADD CONSTRAINT dag_tag_dag_id_fkey FOREIGN KEY (dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: dagrun_dataset_event dagrun_dataset_event_dag_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dagrun_dataset_event
    ADD CONSTRAINT dagrun_dataset_event_dag_run_id_fkey FOREIGN KEY (dag_run_id) REFERENCES public.dag_run(id) ON DELETE CASCADE;


--
-- Name: dagrun_dataset_event dagrun_dataset_event_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dagrun_dataset_event
    ADD CONSTRAINT dagrun_dataset_event_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.dataset_event(id) ON DELETE CASCADE;


--
-- Name: dag_warning dcw_dag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_warning
    ADD CONSTRAINT dcw_dag_id_fkey FOREIGN KEY (dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: dataset_dag_run_queue ddrq_dag_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset_dag_run_queue
    ADD CONSTRAINT ddrq_dag_fkey FOREIGN KEY (target_dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: dataset_dag_run_queue ddrq_dataset_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dataset_dag_run_queue
    ADD CONSTRAINT ddrq_dataset_fkey FOREIGN KEY (dataset_id) REFERENCES public.dataset(id) ON DELETE CASCADE;


--
-- Name: dag_schedule_dataset_reference dsdr_dag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_schedule_dataset_reference
    ADD CONSTRAINT dsdr_dag_id_fkey FOREIGN KEY (dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: dag_schedule_dataset_reference dsdr_dataset_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_schedule_dataset_reference
    ADD CONSTRAINT dsdr_dataset_fkey FOREIGN KEY (dataset_id) REFERENCES public.dataset(id) ON DELETE CASCADE;


--
-- Name: rendered_task_instance_fields rtif_ti_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.rendered_task_instance_fields
    ADD CONSTRAINT rtif_ti_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- Name: task_fail task_fail_ti_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_fail
    ADD CONSTRAINT task_fail_ti_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- Name: task_instance task_instance_dag_run_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance
    ADD CONSTRAINT task_instance_dag_run_fkey FOREIGN KEY (dag_id, run_id) REFERENCES public.dag_run(dag_id, run_id) ON DELETE CASCADE;


--
-- Name: dag_run task_instance_log_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.dag_run
    ADD CONSTRAINT task_instance_log_template_id_fkey FOREIGN KEY (log_template_id) REFERENCES public.log_template(id);


--
-- Name: task_instance_note task_instance_note_ti_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance_note
    ADD CONSTRAINT task_instance_note_ti_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- Name: task_instance_note task_instance_note_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance_note
    ADD CONSTRAINT task_instance_note_user_fkey FOREIGN KEY (user_id) REFERENCES public.ab_user(id);


--
-- Name: task_instance task_instance_trigger_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_instance
    ADD CONSTRAINT task_instance_trigger_id_fkey FOREIGN KEY (trigger_id) REFERENCES public.trigger(id) ON DELETE CASCADE;


--
-- Name: task_map task_map_task_instance_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_map
    ADD CONSTRAINT task_map_task_instance_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- Name: task_reschedule task_reschedule_dr_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_reschedule
    ADD CONSTRAINT task_reschedule_dr_fkey FOREIGN KEY (dag_id, run_id) REFERENCES public.dag_run(dag_id, run_id) ON DELETE CASCADE;


--
-- Name: task_reschedule task_reschedule_ti_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_reschedule
    ADD CONSTRAINT task_reschedule_ti_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- Name: task_outlet_dataset_reference todr_dag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_outlet_dataset_reference
    ADD CONSTRAINT todr_dag_id_fkey FOREIGN KEY (dag_id) REFERENCES public.dag(dag_id) ON DELETE CASCADE;


--
-- Name: task_outlet_dataset_reference todr_dataset_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.task_outlet_dataset_reference
    ADD CONSTRAINT todr_dataset_fkey FOREIGN KEY (dataset_id) REFERENCES public.dataset(id) ON DELETE CASCADE;


--
-- Name: xcom xcom_task_instance_fkey; Type: FK CONSTRAINT; Schema: public; Owner: airflow
--

ALTER TABLE ONLY public.xcom
    ADD CONSTRAINT xcom_task_instance_fkey FOREIGN KEY (dag_id, task_id, run_id, map_index) REFERENCES public.task_instance(dag_id, task_id, run_id, map_index) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

