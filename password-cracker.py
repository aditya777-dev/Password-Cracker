import hashlib
import itertools
import string
import time
import multiprocessing
import threading

# Hashing algorithms
HASH_ALGORITHMS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512
}

# Function to hash a string using a given algorithm
def hash_string(algorithm, password):
    hasher = HASH_ALGORITHMS[algorithm]()
    hasher.update(password.encode('utf-8'))
    return hasher.hexdigest()

# Function to perform brute-force attack
def brute_force_attack(hashed_password, algorithm, charset, length_min, length_max, wordlist=None, start=None, end=None, queue=None):
    try:
        if wordlist:
            #print("Using wordlist...")
            with open(wordlist, 'r') as file:
                words = file.read().splitlines()
            for word in words:
                hashed = hash_string(algorithm, word)
                #print("Checking word:", word)
                #print("Hashed value:", hashed)
                #print("Provided hashed password:", hashed_password)
                if hashed == hashed_password:
                    if queue:
                        queue.put((word, hashed))
                    else:
                        print("Password found:", word)
                        print("Hashed:", hashed)
                    return
                if queue and queue.qsize() > 0:
                    return
        else:
            print("Performing brute-force attack...")
            for length in range(length_min, length_max + 1):
                for combination in itertools.product(charset, repeat=length):
                    password = ''.join(combination)
                    hashed = hash_string(algorithm, password)
                    print("Trying combination:", password)  # Print the combination being tried
                    if hashed == hashed_password:
                        if queue:
                            queue.put((password, hashed))
                        else:
                            print("Password found:", password)
                            print("Hashed:", hashed)
                        return
                    if queue and queue.qsize() > 0:
                        return
                if end and time.time() > end:
                    return
    except Exception as e:
        print("Error during brute-force attack:", e)


# Function to start brute-force attack using multiprocessing
def start_brute_force_multiprocess(hashed_password, algorithm, charset, length_min, length_max, wordlist=None):
    try:
        manager = multiprocessing.Manager()
        queue = manager.Queue()
        start_time = time.time()
        num_cores = multiprocessing.cpu_count()
        processes = []
        chunk_size = length_max // num_cores

        for i in range(num_cores):
            start = i * chunk_size
            end = start + chunk_size
            p = multiprocessing.Process(target=brute_force_attack, args=(hashed_password, algorithm, charset, length_min, length_max, wordlist, start_time + 600, end, queue))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        while not queue.empty():
            password, hashed = queue.get()
            print("Password found:", password)
            print("Hashed:", hashed)
    except Exception as e:
        print("Error during multiprocessing:", e)

# Function to start brute-force attack using multithreading
def start_brute_force_multithread(hashed_password, algorithm, charset, length_min, length_max, wordlist=None):
    try:
        start_time = time.time()
        threads = []
        num_threads = 4

        for i in range(num_threads):
            t = threading.Thread(target=brute_force_attack, args=(hashed_password, algorithm, charset, length_min, length_max, wordlist, start_time + 600, None))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
    except Exception as e:
        print("Error during multithreading:", e)

# Function to optimize wordlist
def optimize_wordlist(wordlist):
    try:
        optimized_words = set()
        with open(wordlist, 'r') as file:
            for line in file:
                for word in line.strip().split():
                    optimized_words.add(word)

        # Write the optimized wordlist back to the file
        with open(wordlist, 'w') as file:
            for word in optimized_words:
                file.write(word + '\n')

        print("Optimized wordlist:", optimized_words)
        return list(optimized_words)
    except FileNotFoundError:
        print("Wordlist file not found.")
        return []
    except Exception as e:
        print("Error reading wordlist file:", e)
        return []

# Main function
def main():
    try:
        algorithm = input("Enter the hashing algorithm (md5, sha1, sha224, sha256, sha384, or sha512): ").lower()
        if algorithm not in HASH_ALGORITHMS:
            print("Invalid algorithm!")
            return

        hashed_password = input("Enter the hashed password: ")
        charset = string.ascii_letters + string.digits + string.punctuation
        length_min = int(input("Enter minimum password length: "))
        length_max = int(input("Enter maximum password length: "))

        wordlist_option = input("Do you want to use a wordlist file? (yes/no): ").lower()
        if wordlist_option == 'yes':
            wordlist = input("Enter the path to the wordlist file: ")
            optimize = input("Do you want to optimize wordlist? This will overrite you existing wordlist file. (yes/no): ")
            if optimize == 'yes':
                optimize_wordlist(wordlist)  # Optimize wordlist
        else:
            wordlist = None

        mode = input("Enter mode (single/multi): ").lower()

        if mode == "multi":
            start_brute_force_multiprocess(hashed_password, algorithm, charset, length_min, length_max, wordlist)
        else:
            start_brute_force_multithread(hashed_password, algorithm, charset, length_min, length_max, wordlist)
    except Exception as e:
        print("Error in main function:", e)

if __name__ == "__main__":
    main()
