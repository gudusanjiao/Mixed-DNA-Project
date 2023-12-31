# Will the pipeline good enough to be applied to a broader utilization?

Testing if the pipeline is suitable with different input. We expect they could still maintain at least family-level resolution. There will be some tunings but no large modifying of the current one. If it is not working, I have to develop it all over again taking the assemble genes idea.

---

As mentioned in the last chapter, I want to do two things to check the ability of our pipeline. The first is to run the pipeline to the unknown mix. Let's start with running HybPiper.

```bash
# similar command lines but do not need to run the while loop
#!/bin/bash
#SBATCH -J hyb_asbl_known_mix
#SBATCH -p nocona
#SBATCH -o log/%x.out
#SBATCH -e log/%x.err
#SBATCH -N 1
#SBATCH -n 32
#SBATCH -t 24:00:00
#SBATCH --mem-per-cpu=3G

hybpiper assemble -t_dna ../raw/mega353.fasta \
        -r ../raw/SSBseq003.trimmed.R1.fastq.gz ../raw/SSBseq002.trimmed.R2.fastq.gz \
        --prefix unknownmix \
        --bwa \
        --cpu 32 \
        -o ../hyb_output
```

It takes 15 min to run. And then I threw it into the pipeline. The phylogeny does not have so many hits left after filtering. However, I found some patterns that suggest the taxonomy information of the unknown mix. Most of the exons seems to come from some Fabids and Malvids species, and may have some of the outgroups (Monocots, basal dicot?). I am now downloading reads  from Kew Garden database that select from the suspicious clade and them run the pipeline again to anchor these species.

The idea is to select one monocot (maybe Poaceae species?), one COM Fabids (Malpighiaceae? I was working on Salicaceae but they are all trees...), one Nitrogen fixer Fabids (Rosaceae?), one Myrtaceae, one Malvaceae, and one outgroup (Asteraceae?). In total, it is 6 species.

I will choose the latest one from each family and only use the PAFTOL source data. Also, I will keep an eye on the number of genes recovered. The material I would like to keep in consistent with silica-dried.

```
Poaceae: Gigantochloa atter ERR7621555
COM Fabids, Irvingiaceae: Irvingia gabonensis ERR4180054
N fixer Fabids, Urticaceae: Boehmeria ramiflora ERR7622000
Myrtaceae: Corymbia ficifolia ERR5034279
Malvaceae: Hildegardia barteri ERR7622285 (Herbarium)
Asteraceae: Bethencourtia palmensis ERR9230212
```

Don't forget to trim the reads!
```bash
while read line
do
fastp -i ../raw/${line}_R1.fastq.gz -I ../raw/${line}_R2.fastq.gz -o ../raw/${line}_trimmed_R1.fastq.gz -O ../raw/${line}_trimmed_R2.fastq.gz -j ../output/${line}.json -h ../output/${line}.html
done < namelist.txt
```
Submitted all the jobs. Wait and probably submit the module 2 tonight.

---

The whole exon pipeline is running for the 6 species. I created the expected topology for the comparison. 

(Gigantochloa_atter, (((Irvingia_gabonensis, Boehmeria_ramiflora), (Corymbia_ficifolia, Hildegardia_barteri)), Bethencourtia_palmensis));

Now, I am going to deal with the unknown mix data. The unknown mix seems to have low numbers of assembled contigs. I will try to lower the criteria in HybPiper assemble process.

Asteraceae: Bethencourtia palmensis ERR9230212 is not working (for unknown reason, I will shift to Monarrhenus pinifolius). Here is the updated Species list and the expected tree:
```
Poaceae: Gigantochloa atter ERR7621555
COM Fabids, Irvingiaceae: Irvingia gabonensis ERR4180054
N fixer Fabids, Urticaceae: Boehmeria ramiflora ERR7622000
Myrtaceae: Corymbia ficifolia ERR5034279
Malvaceae: Hildegardia barteri ERR7622285 (Herbarium)
Asteraceae: Monarrhenus pinifolius ERR7621651

(Gigantochloa_atter, (((Irvingia_gabonensis, Boehmeria_ramiflora), (Corymbia_ficifolia, Hildegardia_barteri)), Monarrhenus pinifolius));
```

The results seem to be overfiltered. I modified the criterion of filtering process. -i 0.8 -> 0.2, -p 0.1 -> 0.4. If this is still too stringent I will also change the critical value of the composition test from 0.05 to 0.01 to rescue some exons from merged data.

---

Back to work on Friday. D20 =18 so ... let's make some real progress to wrap up this week! I have 3 things to try on today:
1. Review the results from the pipeline.
2. Redo hybpiper for unknown mix, then merge it with 8 speices and 6 species selected tree.
3. Find a way to cut the outlier long branches from the tree. Test for the criteria.

Got a bad result from the exon pipeline of 6 species. None of the gene trees share the same topology as expected. I wonder what's going on there. I am running a full contig pipeline now.

I started the rework of hybpiper unknown mix with an additional parameter `--cov_cutoff 4`.

---

The module 2 is extremely affected by large input files (merged exons/contigs). I need to add one seletion step to ensure the robustness of the whole pipeline.

I will offer a better pipeline to get this problem solved in line automatically.

In the meantime, I run the module 3 to unknown mix data with additional parameter and p value. However, selected gene trees still lack of unknown exons, or unknown exons won't group with any known species. I am worried about that the fasta file filtering process may generate some bias. However this works fine with known mix samples. What happened to them? I will run the pool soil to see if they have the same issue or it is just the problem with the unknown mix.

The pooled mix is named SSB001 data. Running HybPiper on it (with `--cov_cutoff 4`).

The pooled soil also has low performance. In 12 gene trees, around 10 of them do not have any unknown exons. The only two have them wiped the known species out because of the abundance. They didn't fall into any known species. I wonder if the very long contigs in the assembly affects the filtering and alignments. I will try to remove the long contigs in the filtering processes.

---

I will run normal HybPiper for pooled soil sample (5th). Then, I hope to test a new filtering criterion to discard the long contigs in exon/contig findings. It might affect the current filtering approaches by losing too many true short hits. I will test the mafft alignment by removing different number of sequences for 3 random genes.

I noticed that the reads file of the unknown mix is pretty small. Averagely, there will be 25MBx2 data for each species we know. I doubt that would create some issues in identifying unknown species. Thus, I think I won't try more on these data.

OK. Additional stuff I noticed is that the exonerate output of data1 (the pooled soil) has been very limited. There are some issues with the SPAde or the Exonerate. It is not the downstream analytical problem currently. I will work on dealing with the HybPiper, or even modifying SPAdes for more recovered contigs.

I am trying to automatically generate an expected tree. I will use the species tree method from iqtree to the astral. 

Also, need to mention here is, I would like to compare the output of contig from known mix and pooled soil. I hope there are some contigs make sense to me compared to a random sequences in the soil sample. I will work a little be late for today.

---

Get SPAde or metaSPAde to run for the pooled soil to see what is really in the sample (other than our targets).

Pool 8 species with 6 species to rebuilt a phylogeny, then test the grouping for the knownmix.

Prepare some slides describing our results.

I update the bash scripts for hybpiper 14 species. Basically, it is to prevent submitting a bunch of jobs and then lower the priority of future jobs. Also, I checked the SPAdes and BBmap manual for merging overlapped reads and then assemble. I will check the data structure then recover the segments from the pooled soil samples.

I will use `BBmerge.sh` to generate the overlapped reads.
```bash
bbmerge-auto.sh in=reads.fq out=merged.fq outu=unmerged.fq ihist=ihist.txt ecct extend2=20 iterations=5
```

And then, take the merged and leftovers to the `SPAdes.py`.
```bash
spades.py --merged merged.fq -s unmerged.fq -t 32 -o SSB01.denovo.fa
```

---

SPAdes output contains too many long contigs. There is one with 23745bp. I checked those longest ones with BLASTN web-based search. It turned out to be a lot of bacteria DNA pieces. I also randomly checked smaller segments assembled. Most of them are prokaryotes and only very few eukaryotes species.

I merged the 8 species data and additional 5 species (Irvingia excluded) to call for a species tree. The pipeline is written here:

```bash
#!/bin/bash
#SBATCH -J contig_pipeline
#SBATCH -p nocona
#SBATCH -o log/%x.out
#SBATCH -e log/%x.err
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -t 24:00:00
#SBATCH --mem-per-cpu=3G

# A pipeline of reconstructing phylogeny trees using exon information from HybPiper output
# Nan Hu, 09/22/2023

# -----
# Constants. Please edit them to match the data structure of your own directory. Dont include the last "/" in the path.
iqtree_dir=~/software/iqtree/iqtree-2.2.2.7-Linux/bin

# A batch run for all genes:
while read gene
do
        # MAFFT alignment and trim over-gapped
        mafft --preservecase --maxiterate 1000 --localpair --thread 64 ${gene}.FNA> ${gene}.aligned.fasta
        trimal -in ${gene}.aligned.fasta -out ${gene}.trimmed.fasta -gt 0.5

        # Tree construction and comparison
        ${iqtree_dir}/iqtree2 -s ${gene}.trimmed.fasta -m MFP -bb 1000 -redo
        nw_ed ${gene}.trimmed.fasta.treefile 'i & b<50' o > ${gene}.collapsed.tre
done < ../shared_genes.txt

cat *.collapsed.tre > merged.collapsed.tre
astral -i merged.collapsed.tre -o ../6species_species.tre
```

It needs to be run under `as_ref_FNA` folder under the output folder of contig full pipeline.

Then, I ran the gene tree selection pipeline to extract the gene tree which matches the species tree using exon information. Filtering criteria is 0.7, 0.1.

I will run the tree test for unknown and known mix to check the topology.

---

Got introduced of Sourmash and Cracker (am I correct?) from the FDA. There are hugh amount of [tutorial](https://sourmash.readthedocs.io/en/latest/) to read. Interestingly, the algorithm about make a rough hash for the query DNA sequences and then quickly comparing each other actually meets up my naive thoughts about how to boost up the species identification process. I was thinking about transfer a DNA sequence into a eigenvalue or eigenvector and then using matrix calculation methods to solve the issue. However, I know very little about linear algebra as well as hash algorithm thus all these fancy thoughts were just a far future plan. I am glad that there is already a toolkit to de-dimension the DNA data.