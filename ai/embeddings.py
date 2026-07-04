import psycopg2
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

conn = psycopg2.connect(
    host = "localhost",
    database = "brand_intelligence",
    user = "postgres",
    password = "vanshika"

)

cursor = conn.cursor()

cursor.execute("""
               Select id, title
               from mentions
               WHERE title IS NIT NULL
               """)

rows = cursor.fetchall()

titles = [row[1] for row in rows]

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)
embeddings = model.encode(titles)

# Clustering
kmeans = KMeans(
    n_clusters=3,
    random_state=42
)

clusters = kmeans.fit_predict(embeddings)

# Print Results
for title, cluster in zip(titles, clusters):
    print(f"Cluster {cluster}: {title}")


