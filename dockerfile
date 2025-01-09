FROM apache/airflow:2.10.4

USER root
#Set the working directory inside the container
#WORKDIR /app

#Copy all files from your working directory to the container
#COPY . /app

#Create tmp/raw folder and set permissions
#Ensure permissions for Airflow user
#RUN mkdir -p /app/dags/tmp/raw && \
    #chown -R airflow:root /app/dags/tmp/raw && \
    #chmod -R 777 /app/dags/tmp/raw

# Ensure permissions for Airflow user
#RUN mkdir -p /app/dags/tmp/transformed_data && \
    #chown -R airflow:root /app/dags/tmp/transformed_data &&  \
    #chmod -R 777 /app/dags/tmp/transformed_data

#RUN mkdir -p /app/dags/tmp/transformed_data && chmod -R 777 /app/dags/tmp/transformed_data

# Install the Spark provider
#RUN pip install apache-airflow-providers-apache-spark




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

# Install Java and Bash
#RUN apt-get update && apt-get install -y --no-install-recommends bash openjdk-11-jdk-headless && \
    #apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for PySpark
#ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
#ENV PATH=$JAVA_HOME/bin:$PATH

# Copy DAGs and other files
COPY requirements.txt /requirements.txt

# Upgrade pip and install packages from requirements.txt
# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
# Revert back to airflow user
#USER airflow

# Expose Airflow's default port
EXPOSE 8080

# Start Airflow webserver using sh
CMD ["sh", "-c", "airflow webserver"]