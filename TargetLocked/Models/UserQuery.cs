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
        public string Url { get; set; }
        public List<DiseaseObject> Diseases { get; set; }
        public List<string> Species { get; set; }
        public double Date_seconds { get; set; }
        public string API { get; set; }
        public List<string> Genes { get; set; }
        public List<string> MutationType { get; set; }
    }

    public class DiseaseObject
    {
        public double score { get; set; }
        public string disease { get; set; }
    }

    public class Gene
    {
        public string chromosome { get; set; }
        public string gene_name { get; set; }
        public int id { get; set; }
    }
}
