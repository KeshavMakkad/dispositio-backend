/*
 * Google Apps Script for syncing classroom definitions from a sheet
 * to the backend Sheets upsert endpoint.
 *
 * Required script properties:
 * - DISPOSITIO_BASE_URL   (example: https://api.example.com)
 * - DISPOSITIO_SHEETS_API_KEY
 *
 * Expected sheet columns (header row):
 * name, columnsCount, maxRows, totalCapacity, setOneCapacity, setTwoCapacity, classLayoutJson
 *
 * classLayoutJson must be valid JSON array of items:
 * [
 *   {"columnName":"A","columnCapacity":10,"columnSet":"set_1"},
 *   {"columnName":"B","columnCapacity":10,"columnSet":"set_2"}
 * ]
 */
function syncClassroomsToDispositio() {
  const props = PropertiesService.getScriptProperties();
  const baseUrl = props.getProperty('DISPOSITIO_BASE_URL');
  const apiKey = props.getProperty('DISPOSITIO_SHEETS_API_KEY');

  if (!baseUrl || !apiKey) {
    throw new Error('Missing script properties: DISPOSITIO_BASE_URL or DISPOSITIO_SHEETS_API_KEY');
  }

  const sheet = SpreadsheetApp.getActiveSheet();
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    throw new Error('No data rows found.');
  }

  const headers = values[0].map(function (h) { return String(h).trim(); });
  const rows = values.slice(1);

  const requiredHeaders = [
    'name',
    'columnsCount',
    'maxRows',
    'totalCapacity',
    'setOneCapacity',
    'setTwoCapacity',
    'classLayoutJson'
  ];

  requiredHeaders.forEach(function (header) {
    if (headers.indexOf(header) === -1) {
      throw new Error('Missing required header: ' + header);
    }
  });

  const idx = {};
  headers.forEach(function (h, i) { idx[h] = i; });

  const classrooms = rows
    .filter(function (row) {
      return String(row[idx.name] || '').trim() !== '';
    })
    .map(function (row, rowOffset) {
      const rowNumber = rowOffset + 2;
      let classLayout;
      try {
        classLayout = JSON.parse(String(row[idx.classLayoutJson] || '[]'));
      } catch (e) {
        throw new Error('Invalid classLayoutJson at row ' + rowNumber + ': ' + e.message);
      }

      return {
        name: String(row[idx.name]).trim(),
        columnsCount: Number(row[idx.columnsCount]),
        maxRows: Number(row[idx.maxRows]),
        totalCapacity: Number(row[idx.totalCapacity]),
        setOneCapacity: Number(row[idx.setOneCapacity]),
        setTwoCapacity: Number(row[idx.setTwoCapacity]),
        classLayout: classLayout
      };
    });

  const payload = {
    classrooms: classrooms
  };

  const response = UrlFetchApp.fetch(baseUrl.replace(/\/$/, '') + '/api/v1/classroom/sheets/upsert', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'X-Sheets-Api-Key': apiKey
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  const status = response.getResponseCode();
  const body = response.getContentText();

  if (status < 200 || status >= 300) {
    throw new Error('Sync failed (' + status + '): ' + body);
  }

  Logger.log('Sync success: ' + body);
}
