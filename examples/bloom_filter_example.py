from redis_data_structures.bloom_filter import BloomFilter


def main():
    # Initialize a Bloom filter with custom parameters
    bloom = BloomFilter(
        expected_elements=1000,  # Expect to store ~1000 elements
        false_positive_rate=0.01,  # 1% false positive rate
        host="localhost",
        port=6379,
        db=0,
    )

    # Key for our Bloom filter in Redis
    filter_key = "email_blacklist"

    # Add some email addresses to the blacklist
    spam_emails = ["spam1@example.com", "spam2@example.com", "badactor@example.com"]

    print("Adding spam emails to blacklist...")
    for email in spam_emails:
        if bloom.add(filter_key, email):
            print(f"Added {email} to blacklist")

    # Check if emails exist in the blacklist
    test_emails = [
        "spam1@example.com",  # Should be found
        "legitimate@example.com",  # Should not be found
        "spam2@example.com",  # Should be found
        "newuser@example.com",  # Should not be found
    ]

    print("\nChecking emails against blacklist...")
    for email in test_emails:
        result = bloom.contains(filter_key, email)
        status = "might be" if result else "is not"
        print(f"Email {email} {status} in the blacklist")

    # Get the size of the Bloom filter
    filter_size = bloom.size()
    print(f"\nBloom filter size: {filter_size} bits")

    # Clear the Bloom filter
    print("\nClearing the Bloom filter...")
    if bloom.clear(filter_key):
        print("Bloom filter cleared successfully")


if __name__ == "__main__":
    main()
