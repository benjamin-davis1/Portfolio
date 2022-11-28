using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using FFDCServiceUI.Data;
using FFDCServiceUI.Models;

namespace FFDCServiceUI.Controllers
{
  public class DataShareSchedulesController : Controller
  {
    private readonly FFDCServiceUIContext _context;

    public DataShareSchedulesController(FFDCServiceUIContext context)
    {
      _context = context;
    }

    // GET: DataShareSchedules
    public async Task<IActionResult> Index()
    {
      return View(await _context.DataShareSchedule.ToListAsync());
    }

    // GET: DataShareSchedules/Details/5
    public async Task<IActionResult> Details(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var dataShareSchedule = await _context.DataShareSchedule
          .FirstOrDefaultAsync(m => m.ID == id);
      if (dataShareSchedule == null)
      {
        return NotFound();
      }

      return View(dataShareSchedule);
    }

    // GET: DataShareSchedules/Create
    public IActionResult Create()
    {
      List<Customer> customers = new List<Customer>();
      customers = (from c in _context.Customer select c).ToList();
      customers.Insert(0, new Customer { ID = 0, Name = "--Select Customer--" });
      ViewBag.message = customers;

      return View();
    }

    // POST: DataShareSchedules/Create
    // To protect from overposting attacks, enable the specific properties you want to bind to, for 
    // more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create([Bind("ID,CustomerID,Level,Environment,RatesEnv,RatesSource,LengthValue,Path,Folder,Frequency,SampleFrequency,Window,LoadTrades,LoadRates,LoadCounterparties")] DataShareSchedule dataShareSchedule)
    {
      if (ModelState.IsValid)
      {
        _context.Add(dataShareSchedule);
        await _context.SaveChangesAsync();
        return RedirectToAction(nameof(Index));
      }
      return View(dataShareSchedule);
    }

    // GET: DataShareSchedules/Edit/5
    public async Task<IActionResult> Edit(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var dataShareSchedule = await _context.DataShareSchedule.FindAsync(id);
      if (dataShareSchedule == null)
      {
        return NotFound();
      }
      return View(dataShareSchedule);
    }

    // POST: DataShareSchedules/Edit/5
    // To protect from overposting attacks, enable the specific properties you want to bind to, for 
    // more details, see http://go.microsoft.com/fwlink/?LinkId=317598.
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(int id, [Bind("ID,CustomerID,Level,Environment,RatesEnv,RatesSource,LengthValue,Path,Folder,Frequency,SampleFrequency,Window,LoadTrades,LoadRates,LoadCounterparties")] DataShareSchedule dataShareSchedule)
    {
      if (id != dataShareSchedule.ID)
      {
        return NotFound();
      }

      if (ModelState.IsValid)
      {
        try
        {
          _context.Update(dataShareSchedule);
          await _context.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
          if (!DataShareScheduleExists(dataShareSchedule.ID))
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
      return View(dataShareSchedule);
    }

    // GET: DataShareSchedules/Delete/5
    public async Task<IActionResult> Delete(int? id)
    {
      if (id == null)
      {
        return NotFound();
      }

      var dataShareSchedule = await _context.DataShareSchedule
          .FirstOrDefaultAsync(m => m.ID == id);
      if (dataShareSchedule == null)
      {
        return NotFound();
      }

      return View(dataShareSchedule);
    }

    // POST: DataShareSchedules/Delete/5
    [HttpPost, ActionName("Delete")]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DeleteConfirmed(int id)
    {
      var dataShareSchedule = await _context.DataShareSchedule.FindAsync(id);
      _context.DataShareSchedule.Remove(dataShareSchedule);
      await _context.SaveChangesAsync();
      return RedirectToAction(nameof(Index));
    }

    private bool DataShareScheduleExists(int id)
    {
      return _context.DataShareSchedule.Any(e => e.ID == id);
    }
  }
}
