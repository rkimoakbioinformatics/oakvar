# CLI Commands

## Setup

    ov system setup

## Run an analysis job

    ov run

## Create annotation reports

    ov report

## Launch a GUI server

    ov gui

## Manage modules

### List modules

	ov module ls
  
### Install modules

	ov module install


### Uninstall modules

	ov module uninstall

### Install system modules

	ov module installbase

### Update modules

	ov module update

### Get information on modules

	ov module info

## Manage store accounts

### Create a store account

    ov store account create

### Delete a store account

    ov store account delete

### Change a store account password

    ov store account change

### Check if logged in on the OakVar store

    ov store account check

### Log in on the OakVar store

    ov store account login

### Log out from the OakVar store

    ov store account logout

### Reset the password of a store account

    ov store account reset

## Publish modules

### Pack a module for registering at the OakVar store

    ov module pack

### Register a module at the OakVar store

    ov store register

## Manage configuration

### Manage modules directory

	ov system md

### Show system configuration

	ov config system

### Show user configuration

    ov config user

## Test modules

	ov util test

## Utilities

### Create an example input file

	ov new exampleinput

### Create an annotation module template

	ov new annotator

### Merge analysis result database files

	ov util mergesqlite

### Filter analysis result database files

	ov util filtersqlite

### Show analysis result database file information

	ov util showsqliteinfo

