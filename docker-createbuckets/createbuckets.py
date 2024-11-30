#!/bin/env python3
import os
import json
import subprocess
from typing import TypedDict


class S3StorageOptions(TypedDict):
    access_key: str
    secret_key: str
    bucket_name: str
    region_name: str
    endpoint_url: str


class DjangoStorages(TypedDict):
    BACKEND: str
    OPTIONS: S3StorageOptions
    QFC_IS_LEGACY: bool


STORAGES: dict[str, DjangoStorages] = json.loads(os.environ["STORAGES"])


for storage_name, storage_config in STORAGES.items():
    print(f"Creating bucket for: {storage_name}", flush=True)

    endpoint_url = storage_config["OPTIONS"]["endpoint_url"]
    access_key = storage_config["OPTIONS"]["access_key"]
    secret_key = storage_config["OPTIONS"]["secret_key"]
    bucket_name = storage_config["OPTIONS"]["bucket_name"]

    subprocess.run(
        f"/usr/bin/mc config host add {storage_name} {endpoint_url} {access_key} {secret_key}",
        shell=True,
        check=True,
    )

    result = subprocess.run(
        f"/usr/bin/mc mb --ignore-existing {storage_name}/{bucket_name}",
        shell=True,
    )

    subprocess.run(
        f"/usr/bin/mc anonymous set download {storage_name}/{bucket_name}/users",
        shell=True,
        check=True,
    )

    if storage_config["QFC_IS_LEGACY"]:
        subprocess.run(
            f"/usr/bin/mc version enable {storage_name}/{bucket_name}",
            shell=True,
            check=True,
        )
