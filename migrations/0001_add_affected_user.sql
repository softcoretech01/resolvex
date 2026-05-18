-- Migration: add affected_user column to ticket_master table

ALTER TABLE ticket_master
    ADD COLUMN affected_user VARCHAR(255) NULL;

-- Run this with your MySQL client or include in deployment scripts.