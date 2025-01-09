FROM apache/airflow:2.10.4

USER root

# Update and install OpenJDK-11 without PPAs
RUN apt-get update \
    && apt-get install -y openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

# Optionally install PySpark if you need to execute Spark jobs locally
RUN pip install pyspark


# Switch to root user
#USER root



# Copy DAGs and other files
COPY requirements.txt /requirements.txt


# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
# Revert back to airflow user
#USER airflow

# Expose Airflow's default port
EXPOSE 8080

# Start Airflow webserver using sh
CMD ["sh", "-c", "airflow webserver"]
