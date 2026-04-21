FROM eclipse-mosquitto:2

# installo client MQTT (già incluso, ma lo assicuriamo)
RUN apk add --no-cache mosquitto-clients

# script di avvio
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
