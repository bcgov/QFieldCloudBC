import logging
from typing import Optional

import django_rq
from qfieldcloud.core.models import ApplyJob, Delta

logger = logging.getLogger(__name__)


def apply_deltas(
    project, user, project_file, overwrite_conflicts, delta_ids=None
) -> Optional[ApplyJob]:
    """Call the orchestrator API to apply a delta file"""

    logger.info(
        f"Requested apply_deltas on {project} with {project_file}; overwrite_conflicts: {overwrite_conflicts}; delta_ids: {delta_ids}"
    )

    job_ids = django_rq.get_queue("delta").started_job_registry.get_job_ids()
    pending_deltas = Delta.objects.filter(
        project=project,
        last_status__in=[
            # do not include deltas with NOT_APPLIED status, as it is a final status
            Delta.Status.PENDING,
            Delta.Status.STARTED,
            Delta.Status.ERROR,
        ],
    ).exclude(
        # exclude jobs that are currently being processed
        applyjob__id__in=job_ids,
    )

    if delta_ids is not None:
        pending_deltas = pending_deltas.filter(pk__in=delta_ids)

    if len(pending_deltas) == 0:
        return None

    apply_job = ApplyJob.objects.create(
        project=project, created_by=user, overwrite_conflicts=overwrite_conflicts
    )

    for delta in pending_deltas:
        apply_job.deltas_to_apply.add(delta)

    return apply_job
