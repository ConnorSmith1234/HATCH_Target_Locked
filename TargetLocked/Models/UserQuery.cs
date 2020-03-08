using System;
using System.Collections.Generic;

namespace TargetLocked.Models
{
    public class UserQuery
    {
        public string QueryString { get; set; }
    }

    public class QueryResponse
    {
        public string Title { get; set; }
        public List<string> Authors { get; set; }
        public string Abstract { get; set; }
        public string URL { get; set; }
        public List<string> Diseases { get; set; }
        public List<string> Species { get; set; }
        public double Date { get; set; }
        public string API { get; set; }
        public List<string> Genes { get; set; }
        public string MutationType { get; set; }
        public static QueryResponse sampleResponse()
        {
            return new QueryResponse
            {
                Title = "The map-based sequence of the rice genome",
                Authors = new List<string>() { "Francis Bacon", "Mike Tyson", "Luke Skywalker" },
                Abstract = "Rice, one of the world's most important food plants, has important syntenic relationships with the other cereal species and is a model plant for the grasses. Here we present a map-based, finished quality sequence that covers 95% of the 389 Mb genome, including virtually all of the euchromatin and two complete centromeres. A total of 37,544 non-transposable-element-related protein-coding genes were identified, of which 71% had a putative homologue in Arabidopsis. In a reciprocal analysis, 90% of the Arabidopsis proteins had a putative homologue in the predicted rice proteome. Twenty-nine per cent of the 37,544 predicted genes appear in clustered gene families. The number and classes of transposable elements found in the rice genome are consistent with the expansion of syntenic regions in the maize and sorghum genomes. We find evidence for widespread and recurrent gene transfer from the organelles to the nuclear chromosomes. The map-based sequence has proven useful for the identification of genes underlying agronomic traits. The additional single-nucleotide polymorphisms and simple sequence repeats identified in our study should accelerate improvements in rice production.\n\n",
                URL = "www.articles.com",
                Diseases = new List<string>() { "arthritis", "cancer", "asthma" },
                Species = new List<string>() { "human", "mouse" },
                Date = 1583610692.440435,
                API = "BioMed",
                Genes = new List<string>() { "FOXP2", "SCA", "PSEN"},
                MutationType = "base substitution"
            };
        }
    }

    public class Gene
    {
        public string chromosome { get; set; }
        public string gene_name { get; set; }
        public int id { get; set; }
    }
}
