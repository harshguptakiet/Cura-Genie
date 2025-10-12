const downloadReport = async () => {
  const response = await fetch("http://127.0.0.1:8000/reports/download-report/test");
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'CuraGenie_Report.pdf';
  link.click();
};

// Call the function
downloadReport();
