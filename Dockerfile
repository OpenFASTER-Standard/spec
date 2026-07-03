# Reproducible build environment for the OpenFASTER specification.
# Bundles Bikeshed (HTML) and WeasyPrint (PDF) plus the native libraries
# WeasyPrint needs, so the spec + PDF build identically on any host (notably
# Windows, where WeasyPrint's native dependencies are otherwise awkward).
#
#   docker build -t openfaster-spec .
#   docker run --rm -v "${PWD}:/spec" openfaster-spec
#
# Outputs index.html and openfaster.pdf back into the mounted working directory.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libfontconfig1 \
        libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /spec

COPY requirements.txt ./
COPY documentation/requirements-spec.txt ./documentation/
RUN pip install --no-cache-dir -r requirements.txt -r documentation/requirements-spec.txt \
    && bikeshed update

COPY . .

CMD ["sh", "-c", "python generate_template.py && bikeshed --allow-nonlocal-files --die-on=link-error spec documentation/index.bs documentation/index.html && weasyprint --stylesheet documentation/print.css documentation/index.html documentation/openfaster.pdf && echo 'Built documentation/index.html and documentation/openfaster.pdf'"]
