import psycopg2
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

# Database Connection
conn = psycopg2.connect(
    host="localhost",
    database="brand_intelligence",
    user="postgres",
    password="vanshika"
)

cursor = conn.cursor()

# Brand Input
brand_name = input("Enter Brand Name: ")

# Fetch Posts for Selected Brand
cursor.execute("""
SELECT m.id, m.title
FROM mentions m
JOIN brands b
ON m.brand_id = b.id
WHERE LOWER(b.brand_name) = LOWER(%s)
""", (brand_name,))

rows = cursor.fetchall()

if len(rows) == 0:
    print("No posts found for this brand.")
    conn.close()
    exit()

titles = [row[1] for row in rows]

# Embedding Model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

embeddings = model.encode(titles)

# Clustering
n_clusters = min(3, len(titles))

kmeans = KMeans(
    n_clusters=n_clusters,
    random_state=42,
    n_init=10
)

clusters = kmeans.fit_predict(embeddings)

# Save Cluster IDs to Database
for row, cluster in zip(rows, clusters):

    mention_id = row[0]
    title = row[1]

    print(f"Cluster {cluster}: {title}")

    cursor.execute(
        """
        UPDATE mentions
        SET cluster_id = %s
        WHERE id = %s
        """,
        (int(cluster), mention_id)
    )

conn.commit()

print("\nCluster IDs saved successfully!")

conn.close()