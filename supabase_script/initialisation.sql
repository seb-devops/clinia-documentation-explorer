-- Enable the pgvector extension
create extension if not exists vector;

-- Create the documentation chunks table
create table site_pages (
    id bigserial primary key,
    url varchar not null,
    chunk_number integer not null,
    title varchar not null,
    summary varchar not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    fts tsvector generated always as (to_tsvector('english', content)) stored,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    unique(url, chunk_number)
);

SET maintenance_work_mem = '128MB';
create index on site_pages using ivfflat (embedding vector_ip_ops);
SET maintenance_work_mem = '32MB';

-- Create an index on metadata for faster filtering
create index idx_site_pages_metadata on site_pages using gin (metadata);

-- Enable RLS on the table
alter table site_pages enable row level security;

-- Create a policy that allows anyone to read
create policy "Allow public read access"
  on site_pages
  for select
  to public
  using (true);-- Enable the pgvector extension
create extension if not exists vector;

-- Create the documentation chunks table
create table site_pages (
    id bigserial primary key,
    url varchar not null,
    chunk_number integer not null,
    title varchar not null,
    summary varchar not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    fts tsvector generated always as (to_tsvector('english', content)) stored,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    unique(url, chunk_number)
);

SET maintenance_work_mem = '128MB';
create index on site_pages using ivfflat (embedding vector_ip_ops);
SET maintenance_work_mem = '32MB';

-- Create an index on metadata for faster filtering
create index idx_site_pages_metadata on site_pages using gin (metadata);

-- Enable RLS on the table
alter table site_pages enable row level security;

-- Create a policy that allows anyone to read
create policy "Allow public read access"
  on site_pages
  for select
  to public
  using (true);