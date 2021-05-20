use rumqttc::{self, Client, LastWill, MqttOptions, QoS, Event, Packet, ConnectReturnCode};
use std::thread;
use std::time::Duration;
use std::fmt;
use thiserror::Error;
use slog::{error};

// Much was found in https://github.com/ckauhaus/esera-mqtt/blob/main/src/mqtt.rs

#[derive(Error, Debug)]
pub enum Error {
    #[error("Failed to connect to MQTT broker at {0}: {1}")]
    Connect(String, #[source] rumqttc::ConnectionError),
    #[error("Lost connection to MQTT broker")]
    Disconnected,
    #[error("Failed to subscribe topic {0}: {1}")]
    Subscribe(String, #[source] rumqttc::ClientError),
    #[error("Failed to publish MQTT message: {0}")]
    Send(#[from] rumqttc::ClientError),
    #[error("Failed to decode UTF-8 message payload: {0}")]
    Utf8(#[from] std::string::FromUtf8Error),
    // #[error(transparent)]
    // Channel(#[from] channel::SendError<MqttMsg>),
}

type Result<T, E = Error> = std::result::Result<T, E>;

#[derive(Debug, Clone, PartialEq)]
pub enum MqttMsg {
    Pub {
        topic: String,
        payload: String,
        retain: bool,
    },
    Sub {
        topic: String,
    },
    Reconnected,
}

impl MqttMsg {
    pub fn new<S: Into<String>, P: ToString>(topic: S, payload: P) -> Self {
        Self::Pub {
            topic: topic.into(),
            payload: payload.to_string(),
            retain: false,
        }
    }

    pub fn retain<S: Into<String>, P: ToString>(topic: S, payload: P) -> Self {
        Self::Pub {
            topic: topic.into(),
            payload: payload.to_string(),
            retain: true,
        }
    }

    pub fn sub<S: Into<String>>(topic: S) -> Self {
        Self::Sub {
            topic: topic.into(),
        }
    }

    /// Returns topic of a message. Panics if this message does not contain a topic.
    pub fn topic(&self) -> &str {
        match self {
            Self::Pub { ref topic, .. } => topic,
            Self::Sub { ref topic } => topic,
            _ => panic!(
                "Attempted to call MqttMsg::topic of a message without payload ({:?})",
                self
            ),
        }
    }

    /// Returns payload of a publish message. Panics if this is not a publish message.
    pub fn payload(&self) -> &str {
        match self {
            Self::Pub { ref payload, .. } => payload,
            _ => panic!(
                "Attempted to call MqttMsg::payload of a non-publish message ({:?})",
                self
            ),
        }
    }

    /// Returns true if this is a publish message which fits topic pattern as per MQTT match
    /// syntax.
    pub fn matches(&self, topic_pattern: &str) -> bool {
        if let Self::Pub { topic, .. } = self {
            rumqttc::matches(topic, topic_pattern)
        } else {
            false
        }
    }
}

impl fmt::Display for MqttMsg {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Pub {
                topic,
                payload,
                retain,
            } => write!(
                f,
                "{} {}{}",
                topic,
                payload,
                if *retain { " (retain)" } else { "" }
            ),
            Self::Sub { topic } => write!(f, "Subscribe {}", topic),
            Self::Reconnected => write!(f, "Reconnected to broker"),
        }
    }
}

fn process_packet(pck: Packet) -> Result<()> {
    match pck {
        Packet::Publish(p) => {
            let msg = MqttMsg::new(p.topic, String::from_utf8(p.payload.to_vec())?);
            // println!("==< {:?}", msg);
            // tx.send(msg).map_err(Error::from)
            println!("<<< {}", msg.payload());
            Ok(())
        }
        Packet::Disconnect => Err(Error::Disconnected),
        Packet::ConnAck(rumqttc::ConnAck {
            code: ConnectReturnCode::Success,
            ..
        }) => {
            // info!(log, "Reconnected to MQTT broker");
            // tx.send(MqttMsg::Reconnected).map_err(Error::from)
            Ok(())
        }
        _ => Ok(()),
    }
}

fn main() {
    // pretty_env_logger::init();

    let mut retry = 200;

    let mut mqttoptions = MqttOptions::new("test-1", "mqtt.eclipseprojects.io", 1883);
    let will = LastWill::new("hvable", "good bye", QoS::AtMostOnce, false);
    mqttoptions.set_keep_alive(5).set_last_will(will);
    let (client, mut connection) = Client::new(mqttoptions, 10);

    // The following would publish 10 test messages.
    // This has been commented out, as I would only to act as a listener.
    //
    thread::spawn(move || publish(client));

    for (i, notification) in connection.iter().enumerate() {
        // For debug purposes, print the whole notification:
        println!("{}. Notification = {:?}", i, notification);
        match notification {
            Ok(Event::Incoming(pck)) => match process_packet(pck) {
                Err(_) => {
                    println!("MQTT channel disconnected");
                    return;
                }
                Ok(_) => (),
            },
            Ok(Event::Outgoing(_)) => (),
            Err(e) => {
                println!("{}, reconnecting in {} ms", e, retry);
                thread::sleep(Duration::from_millis(retry));
                if retry < 10_000 {
                    retry = retry * 6 / 5;
                }
            }
        }
    }

    println!("Done with the stream!!");
}

fn publish(mut client: Client) {
    client.subscribe("hvable", QoS::AtMostOnce).unwrap();
    for i in 0..10 {
        let payload = format!("message#{}", i);
        let topic = format!("hvable");
        let qos = QoS::AtLeastOnce;

        client.publish(topic, qos, true, payload).unwrap();
    }

    thread::sleep(Duration::from_secs(1));
}
