
FROM python:2.7
COPY . /app
WORKDIR /app
RUN pip install -r requirments.txt
ENTRYPOINT ["python"]
EXPOSE 8888
CMD ["my_script.py"]
