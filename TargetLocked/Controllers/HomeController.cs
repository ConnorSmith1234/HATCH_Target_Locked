using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using TargetLocked.DB;
using TargetLocked.Models;

namespace TargetLocked.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;
        private readonly DatabaseContext _databaseContext = new DatabaseContext();
        private readonly string _pythonLocation;

        public HomeController(ILogger<HomeController> logger, IConfiguration configuration)
        {
            _logger = logger;
            _pythonLocation = configuration.GetValue<string>("PythonLocation");
        }

        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Autofill([FromBody]string queryPortion)
        {
            List<Gene> query_response = _databaseContext.Genes.Where(x => x.gene_name.Contains(queryPortion.ToUpper())).ToList();
            return Json(query_response);
        }

        [HttpPost]
        public IActionResult Search([FromBody]UserQuery query)
        {
            string directory = Path.Combine(Directory.GetCurrentDirectory(), "SampleData", "search_results1.json");
            var myJSONString = System.IO.File.ReadAllText(directory);
            List<QueryResponse> queryResponse = JsonConvert.DeserializeObject<List<QueryResponse>>(myJSONString);
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = Path.Combine(_pythonLocation, "python.exe");
            start.Arguments = string.Format("\"" + Path.Combine(Directory.GetCurrentDirectory(), "query.py") + "\" --query {0}\"", query.QueryString);
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string stderr = process.StandardError.ReadToEnd();
                    string result = reader.ReadToEnd();
                    Debug.WriteLine(result);
                    return Json(result);
                }
            }
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
