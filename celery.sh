#!/bin/bash

watchmedo auto-restart --directory=./webapp --pattern=*.py --recursive -- celery -A webapp.celery_entry_point worker
