from connectors.papers.arxiv import ArxivConnector
from connectors.newsletters.rss import RssNewsletterConnector
from connectors.podcasts.spotify import SpotifyConnector
from connectors.youtube import YouTubeConnector

CONNECTOR_REGISTRY = {
    "papers": {
        "arxiv": {
            "class": ArxivConnector,
            "display_name": "arXiv",
            "required_fields": ["categories"],
        },
    },
    "newsletters": {
        "rss": {
            "class": RssNewsletterConnector,
            "display_name": "RSS-based Newsletter",
            "required_fields": ["feed_url"],
        },
    },
    "podcasts": {
        "spotify": {
            "class": SpotifyConnector,
            "display_name": "Spotify Podcasts",
            "required_fields": ["feed_url"],
        },
    },
    "videos": {
        "youtube": {
            "class": YouTubeConnector,
            "display_name": "YouTube",
            "required_fields": ["api_key", "channels"],
        }
    }
}

