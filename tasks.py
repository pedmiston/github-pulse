#!/usr/bin/env python3
import gzip

import json
import requests
import pandas
import invoke

pkg = 'githubarchive'


@invoke.task
def get_data(ctx):
    """Download data from githubarchive.org to the R pkg."""
    src = 'http://data.githubarchive.org/{key}.json.gz'
    dst = '{pkg}/data-raw/{key}.csv'
    key = '2015-01-01-15'

    response = requests.get(src.format(key=key))
    blob = gzip.decompress(response.content).decode('utf-8')
    activity = pandas.DataFrame({'events': blob.splitlines()})

    data = activity.events.apply(json.loads)
    activity['type'] = data.apply(lambda x: x['type'])
    activity['created_at'] = data.apply(lambda x: x['created_at'])

    activity.to_csv(dst.format(pkg=pkg, key=key), index=False)


@invoke.task
def save_as(ctx):
    """Process the raw data and use it in the R pkg."""
    cmd = 'cd {pkg} && Rscript data-raw/save-as.R'
    invoke.run(cmd.format(pkg=pkg))
