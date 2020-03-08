using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using TargetLocked.DB;
using TargetLocked.Models;

namespace TargetLocked.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;
        private readonly DatabaseContext _databaseContext = new DatabaseContext();

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
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
            return Json(new List<QueryResponse>() { QueryResponse.sampleResponse()});
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
