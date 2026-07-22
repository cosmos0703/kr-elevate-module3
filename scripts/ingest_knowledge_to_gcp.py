#!/usr/bin/env python3
"""
CLI script to ingest local knowledge base markdown files into Google Cloud Storage
and trigger Vertex AI Search (Discovery Engine) / Vertex AI RAG Corpus imports.

Usage:
  python scripts/ingest_knowledge_to_gcp.py [--dry-run]
"""
import argparse
import glob
import logging
import os
import sys

# Ensure agent module is loadable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.config import (
    GCS_KNOWLEDGE_BUCKET,
    GOOGLE_CLOUD_PROJECT,
    VERTEX_SEARCH_DATASTORE_ID,
    VERTEX_SEARCH_LOCATION,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge"))


def scan_knowledge_files():
    """Scans and lists markdown policy files in the knowledge directory, excluding non-policy files."""
    pattern = os.path.join(KNOWLEDGE_DIR, "**/*.md")
    excluded = {"README.md", "log.md"}
    files = [f for f in glob.glob(pattern, recursive=True) if os.path.basename(f) not in excluded]
    return files


def upload_to_gcs(bucket_name: str, files: list, dry_run: bool = False) -> bool:
    """Uploads scanned files to Google Cloud Storage bucket with normalized GCS object paths."""
    if not files:
        logger.error("No policy files discovered to upload.")
        return False

    logger.info(f"Preparing to upload {len(files)} files to gs://{bucket_name}/knowledge/...")
    if dry_run:
        for f in files:
            rel = os.path.relpath(f, KNOWLEDGE_DIR).replace("\\", "/")
            logger.info(f"[DRY-RUN] Uploading {f} -> gs://{bucket_name}/knowledge/{rel}")
        return True

    try:
        from google.cloud import storage
        from google.api_core.exceptions import NotFound

        client = storage.Client(project=GOOGLE_CLOUD_PROJECT)
        try:
            bucket = client.get_bucket(bucket_name)
            logger.info(f"Using existing GCS bucket: gs://{bucket_name}")
        except NotFound:
            logger.info(f"Bucket gs://{bucket_name} not found. Creating new bucket in location 'us-central1'...")
            bucket = client.create_bucket(bucket_name, location="us-central1")
            logger.info(f"Successfully created bucket gs://{bucket_name}")

        for f in files:
            rel = os.path.relpath(f, KNOWLEDGE_DIR).replace("\\", "/")
            blob = bucket.blob(f"knowledge/{rel}")
            blob.upload_from_filename(f)
            logger.info(f"Uploaded {f} -> gs://{bucket_name}/knowledge/{rel}")
        return True
    except Exception as e:
        logger.error(f"GCS Upload failed: {e}")
        logger.info("Ensure GCP Application Default Credentials (ADC) are set and google-cloud-storage is installed.")
        return False


def trigger_discovery_engine_import(dry_run: bool = False) -> bool:
    """Triggers asynchronous import into Vertex AI Search Data Store."""
    logger.info(
        f"Triggering Discovery Engine document import for datastore '{VERTEX_SEARCH_DATASTORE_ID}' in '{VERTEX_SEARCH_LOCATION}'..."
    )
    if dry_run:
        logger.info("[DRY-RUN] Discovery Engine ImportTrigger skipped.")
        return True

    try:
        from google.cloud import discoveryengine_v1 as discoveryengine
        from google.api_core.exceptions import NotFound

        # Ensure DataStore exists before importing
        ds_client = discoveryengine.DataStoreServiceClient()
        parent_collection = f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{VERTEX_SEARCH_LOCATION}/collections/default_collection"
        data_store_path = ds_client.data_store_path(
            project=GOOGLE_CLOUD_PROJECT,
            location=VERTEX_SEARCH_LOCATION,
            data_store=VERTEX_SEARCH_DATASTORE_ID,
        )
        try:
            ds_client.get_data_store(name=data_store_path)
            logger.info(f"Using existing Discovery Engine DataStore: {VERTEX_SEARCH_DATASTORE_ID}")
        except Exception:
            logger.info(f"DataStore '{VERTEX_SEARCH_DATASTORE_ID}' not found. Creating Discovery Engine DataStore...")
            data_store = discoveryengine.DataStore(
                display_name="Altostrat HR Policy Datastore",
                industry_vertical=discoveryengine.IndustryVertical.GENERIC,
                solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
                content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
            )
            op = ds_client.create_data_store(
                parent=parent_collection,
                data_store=data_store,
                data_store_id=VERTEX_SEARCH_DATASTORE_ID,
            )
            logger.info(f"DataStore creation operation started: {op.operation.name}")
            op.result()
            logger.info(f"Successfully created DataStore '{VERTEX_SEARCH_DATASTORE_ID}'")

        client = discoveryengine.DocumentServiceClient()
        parent = client.branch_path(
            project=GOOGLE_CLOUD_PROJECT,
            location=VERTEX_SEARCH_LOCATION,
            data_store=VERTEX_SEARCH_DATASTORE_ID,
            branch="default_branch",
        )
        # Valid single-star GCS URI wildcard for Discovery Engine
        gcs_uri = f"gs://{GCS_KNOWLEDGE_BUCKET}/knowledge/*"

        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[gcs_uri],
            ),
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )
        operation = client.import_documents(request=request)
        logger.info(f"Import documents operation started: {operation.operation.name}")
        return True
    except Exception as e:
        logger.error(f"Discovery Engine Import failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ingest HR Policy documents to Google Cloud RAG Engine.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate upload and import actions without executing GCP API calls.")
    args = parser.parse_args()

    files = scan_knowledge_files()
    logger.info(f"Discovered {len(files)} policy markdown documents in {KNOWLEDGE_DIR}.")

    if not files:
        logger.error("No valid policy files found. Exiting with failure status.")
        sys.exit(1)

    success_upload = upload_to_gcs(GCS_KNOWLEDGE_BUCKET, files, dry_run=args.dry_run)
    if not success_upload:
        logger.error("GCS Upload failed. Exiting with failure status.")
        sys.exit(1)

    success_import = trigger_discovery_engine_import(dry_run=args.dry_run)
    if not success_import:
        logger.error("Discovery Engine Import trigger failed. Exiting with failure status.")
        sys.exit(1)

    logger.info("Ingestion script workflow completed successfully.")


if __name__ == "__main__":
    main()
