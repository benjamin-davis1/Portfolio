using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using FFDCServiceUI.Data;
using FFDCServiceUI.Models;
using System.Data.SqlClient;

namespace FFDCServiceUI.Controllers
{
  public class EmailMonitorsController : Controller
  {
    private readonly FFDCServiceUIContext _context;
    public EmailMonitorsController(FFDCServiceUIContext context)
    {
      _context = context;
    }


    // GET: EmailMonitors
    public async Task<IActionResult> Index()
    {
      return View(await _context.EmailMonitor.ToListAsync());
    }

    // GET: EmailMonitors/Details/5
    public async Task<IActionResult> Details(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var emailMonitor = await _context.EmailMonitor
          .FirstOrDefaultAsync(m => m.ID == id);
      if (emailMonitor == null)
      {
        return NotFound();
      }

      return View(emailMonitor);
    }

    // GET: EmailMonitors/Create
    public IActionResult Create()
    {
      List<Customer> customers = new List<Customer>();
      customers = (from c in _context.Customer select c).ToList();
      customers.Insert(0, new Customer { ID = 0, Name = "--Select Customer--" });
      ViewBag.message = customers;

      List<DataShareSchedule> dataShareSchedules = new List<DataShareSchedule>();
      dataShareSchedules = (from b in _context.DataShareSchedule select b).ToList();
      dataShareSchedules.Insert(0, new DataShareSchedule { ID = 0, RatesEnv = "--Select Data Share Schedule--" });
      ViewBag.dataShareSchedules = dataShareSchedules;
      return View();
    }

    // POST: EmailMonitors/Create
    // To protect from overposting attacks, enable the specific properties you want to bind to, for 
    // more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create([Bind("ID,CustomerID,Email,Name,DataShareScheduleID")] EmailMonitor emailMonitor)
    {
      if (ModelState.IsValid)
      {
        _context.Add(emailMonitor);
        await _context.SaveChangesAsync();
        return RedirectToAction(nameof(Index));
      }
      return View(emailMonitor);
    }

    // GET: EmailMonitors/Edit/5
    public async Task<IActionResult> Edit(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var emailMonitor = await _context.EmailMonitor.FindAsync(id);
      if (emailMonitor == null)
      {
        return NotFound();
      }
      return View(emailMonitor);
    }

    // POST: EmailMonitors/Edit/5
    // To protect from overposting attacks, enable the specific properties you want to bind to, for 
    // more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(int id, [Bind("ID,CustomerID,Email,Name,DataShareScheduleID")] EmailMonitor emailMonitor)
    {
      if (id != emailMonitor.ID)
      {
        return NotFound();
      }

      if (ModelState.IsValid)
      {
        try
        {
          _context.Update(emailMonitor);
          await _context.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
          if (!EmailMonitorExists(emailMonitor.ID))
          {
            return NotFound();
          }
          else
          {
            throw;
          }
        }
        return RedirectToAction(nameof(Index));
      }
      return View(emailMonitor);
    }

    // GET: EmailMonitors/Delete/5
    public async Task<IActionResult> Delete(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var emailMonitor = await _context.EmailMonitor
          .FirstOrDefaultAsync(m => m.ID == id);
      if (emailMonitor == null)
      {
        return NotFound();
      }

      return View(emailMonitor);
    }

    // POST: EmailMonitors/Delete/5
    [HttpPost, ActionName("Delete")]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DeleteConfirmed(int id)
    {
      var emailMonitor = await _context.EmailMonitor.FindAsync(id);
      _context.EmailMonitor.Remove(emailMonitor);
      await _context.SaveChangesAsync();
      return RedirectToAction(nameof(Index));
    }

    private bool EmailMonitorExists(int id)
    {
      return _context.EmailMonitor.Any(e => e.ID == id);
    }
  }
}
