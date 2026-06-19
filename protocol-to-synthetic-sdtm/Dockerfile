FROM mediforce-golden-image

ARG CDISC_RULES_ENGINE_REF=v0.16.0

RUN git clone --depth 1 --branch "${CDISC_RULES_ENGINE_REF}" https://github.com/cdisc-org/cdisc-rules-engine.git /app/cdisc-rules-engine \
 && pip3 install --no-cache-dir --break-system-packages -r /app/cdisc-rules-engine/requirements.txt \
 && mkdir -p /app/cdisc-rules-engine/venv/bin \
 && ln -s "$(command -v python3)" /app/cdisc-rules-engine/venv/bin/python

ENV CORE_ENGINE=/app/cdisc-rules-engine

COPY mcp /app/mcp
RUN pip3 install --no-cache-dir --break-system-packages /app/mcp/ctgov /app/mcp/cdisclib

COPY test /app/protocol-to-synthetic-sdtm/test
COPY container/run_stage.py /app/run_stage.py

WORKDIR /workspace
