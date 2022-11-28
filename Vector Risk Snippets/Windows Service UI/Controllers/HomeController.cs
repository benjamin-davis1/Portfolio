using FFDCServiceUI.Data;
using FFDCServiceUI.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;
using System.Data.SqlClient;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;

namespace FFDCServiceUI.Controllers
{
  public class HomeController : Controller
  {
    SqlCommand com = new SqlCommand();
    SqlDataReader dr;
    SqlConnection con = new SqlConnection();
    List<DataShareDelivery> dataShareDeliveries = new List<DataShareDelivery>();
    List<DataShareLog> dataShareLogs = new List<DataShareLog>();

    private readonly ILogger<HomeController> _logger;
    private readonly FFDCServiceUIContext _context;
    public HomeController(ILogger<HomeController> logger, FFDCServiceUIContext context)
    {
      _logger = logger;
      con.ConnectionString = FFDCServiceUI.Properties.Resources.ConnectionString;
      _context = context;
    }

    /*    public IActionResult Index()
        {
          FetchDataShareLogs();
          return View(dataShareLogs);
        }*/

    public async Task<IActionResult> Index(string sortOrder)
    {
      ViewBag.IDSortParm = sortOrder == "ID" ? "ID_desc" : "ID";
      ViewBag.ScheduleIDSortParm = sortOrder == "ScheduleID" ? "ScheduleID_desc" : "ScheduleID";
      ViewBag.ActivitySortParm = sortOrder == "Activity" ? "Activity_desc" : "Activity";
      ViewBag.FilenameSortParm = sortOrder == "Filename" ? "Filename_desc" : "FileName";
      ViewBag.LoadStartedSortParm = sortOrder == "LoadStarted" ? "LoadStarted_desc" : "LoadStarted";
      ViewBag.LoadEndedSortParm = sortOrder == "LoadEnded" ? "LoadEnded_desc" : "LoadEnded";
      ViewBag.SucceededSortParm = sortOrder == "Succeeded" ? "Succeeded_desc" : "Succeeded";
      ViewBag.ErrorMsgSortParm = sortOrder == "ErrorMsg" ? "ErrorMsg_desc" : "ErrorMsg";

      var dataShareLogs = from s in _context.DataShareLog
                         select s;

      switch (sortOrder)
      {
        case "ID_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.ID);
          break;
        case "ID":
          dataShareLogs = dataShareLogs.OrderBy(s => s.ID);
          break;
        case "ScheduleID":
          dataShareLogs = dataShareLogs.OrderBy(s => s.ScheduleID);
          break;
        case "ScheduleID_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.ScheduleID);
          break;
        case "Activity":
          dataShareLogs = dataShareLogs.OrderBy(s => s.Activity);
          break;
        case "Activity_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.Activity);
          break;
        case "Filename":
          dataShareLogs = dataShareLogs.OrderBy(s => s.Filename);
          break;
        case "Filename_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.Filename);
          break;
        case "LoadStarted":
          dataShareLogs = dataShareLogs.OrderBy(s => s.LoadStarted);
          break;
        default:
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.LoadStarted);
          break;
        case "LoadEnded":
          dataShareLogs = dataShareLogs.OrderBy(s => s.LoadEnded);
          break;
        case "LoadEnded_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.LoadEnded);
          break;
        case "Succeeded":
          dataShareLogs = dataShareLogs.OrderBy(s => s.Succeeded);
          break;
        case "Succeeded_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.Succeeded);
          break;
        case "ErrorMsg":
          dataShareLogs = dataShareLogs.OrderBy(s => s.ErrorMsg);
          break;
        case "ErrorMsg_desc":
          dataShareLogs = dataShareLogs.OrderByDescending(s => s.ErrorMsg);
          break;

      }
      return View(await dataShareLogs.ToListAsync());
    }

    public async Task<IActionResult> DataShareDeliveryView(string sortOrder)
    {
      ViewBag.IDSort = sortOrder == "id" ? "id_desc" : "id";
      ViewBag.ScheduleIDSort = sortOrder == "scheduleID" ? "scheduleID_desc" : "scheduleID";
      ViewBag.LoggedAtSort = sortOrder == "LoggedAt" ? "LoggedAt_desc" : "LoggedAt";

      var dataShareDeliveries = from c in _context.DataShareDelivery
                                select c;

      switch (sortOrder)
      {
        case "id_desc":
          dataShareDeliveries = dataShareDeliveries.OrderByDescending(s => s.ID);
          break;
        case "id":
          dataShareDeliveries = dataShareDeliveries.OrderBy(s => s.ID);
          break;
        case "scheduleID_desc":
          dataShareDeliveries = dataShareDeliveries.OrderByDescending(s => s.ScheduleID);
          break;
        case "scheduleID":
          dataShareDeliveries = dataShareDeliveries.OrderBy(s => s.ScheduleID);
          break;
        default:
          dataShareDeliveries = dataShareDeliveries.OrderByDescending(s => s.LoggedAt);
          break;
        case "LoggedAt":
          dataShareDeliveries = dataShareDeliveries.OrderBy(s => s.LoggedAt);
          break;
      }

      return View(await dataShareDeliveries.ToListAsync());
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
