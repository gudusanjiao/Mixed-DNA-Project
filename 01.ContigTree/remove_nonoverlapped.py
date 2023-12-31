import argparse
from Bio import SeqIO
from Bio.Align import PairwiseAligner
from multiprocessing import Pool

def calculate_sequence_stats(fasta_file, min_overlapped_length_proportion_to_mean):
    seq_lengths = []
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq_lengths.append(len(record.seq))

    if not seq_lengths:
        print("No sequences found in the input file.")
        return

    average_length = sum(seq_lengths) / len(seq_lengths) * min_overlapped_length_proportion_to_mean
    return average_length

def is_overlapping(args):
    seq1, seq2, min_overlap = args
    aligner = PairwiseAligner()
    alignments = aligner.align(seq1, seq2)
    match_count = sum(a == b for a, b in zip(*alignments[0]))
    return match_count >= min_overlap

def remove_non_overlapping(input_file, output_file, removed_file, num_threads, min_overlapped_portion, min_overlapped_length_proportion_to_mean):
    records = list(SeqIO.parse(input_file, "fasta"))
    overlapping_records = []
    removed_records = []
    min_overlap = calculate_sequence_stats(input_file, min_overlapped_length_proportion_to_mean)
    with Pool(num_threads) as pool:
        for i in range(len(records)):
            args = [(str(records[i].seq), str(records[j].seq), min_overlap) for j in range(len(records)) if i != j]
            results = pool.map(is_overlapping, args)
            if sum(results) >= len(records) * min_overlapped_portion:
                overlapping_records.append(records[i])
            else:
                removed_records.append(records[i])
    SeqIO.write(overlapping_records, output_file, "fasta")
    SeqIO.write(removed_records, removed_file, "fasta")
    print(f"Removed {len(removed_records)} sequences")

def main():
    parser = argparse.ArgumentParser(description='Remove non-overlapping sequences from a FASTA file.')
    parser.add_argument('input_file', type=str, help='Input FASTA file')
    parser.add_argument('output_file', type=str, help='Output FASTA file for overlapping sequences')
    parser.add_argument('removed_file', type=str, help='Output FASTA file for removed sequences')
    parser.add_argument('-i', '--min_overlapped_length_proportion_to_mean', type=float, default=1.0,
                        help='The minimum overlapped length proportion to the average length of input files')
    parser.add_argument('-t', '--num_threads', type=int, default=1,
                        help='Number of threads to use')
    parser.add_argument('-p', '--min_overlapped_portion', type=float, default=0.1,
                        help='Portion of input sequences for a query sequence need to overlap')
    args = parser.parse_args()
    remove_non_overlapping(args.input_file, args.output_file, args.removed_file,
                           args.num_threads, args.min_overlapped_portion,
                           args.min_overlapped_length_proportion_to_mean)

if __name__ == "__main__":
    main()
