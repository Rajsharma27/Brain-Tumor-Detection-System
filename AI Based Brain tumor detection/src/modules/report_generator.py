from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

load_dotenv()

app = FastAPI(title="Report Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def generate_report(prediction, patient_info):

    try:
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
You are an expert medical AI assistant specializing in brain tumor analysis and diagnosis. 
Generate a comprehensive and professional medical report based on the following patient information:

PATIENT DETAILS:
- Name: {patient_info.get('name', 'N/A')}
- Age: {patient_info.get('age', 'N/A')} years
- Gender: {patient_info.get('gender', 'N/A')}
- Reported Symptoms: {patient_info.get('symptoms', 'Not specified')}

AI ANALYSIS RESULTS:
- Prediction: {prediction}
- Confidence Score: {patient_info.get('confidence', 0) * 100:.1f}%

Please provide a detailed medical report with the following THREE sections:

1. CLINICAL DESCRIPTION:
Provide a detailed medical analysis of the AI prediction. Explain what the prediction means, 
the characteristics of the identified condition, potential implications, and why this diagnosis 
is significant. Include context about how the symptoms relate to the prediction.

2. RECOMMENDED PRECAUTIONS:
List specific, actionable medical precautions and recommended next steps. Include:
- Immediate actions to take
- Medical specialist consultations needed
- Tests or imaging studies to consider
- Lifestyle modifications
- When to seek emergency care

3. THINGS TO REMEMBER:
Provide important points the patient should keep in mind, including:
- Understanding the diagnosis
- Importance of follow-up care
- Medication compliance (if applicable)
- Support resources
- Importance of consulting healthcare professionals

Format your response EXACTLY as follows (use these exact headers):

CLINICAL DESCRIPTION:
[Your detailed clinical analysis here]

RECOMMENDED PRECAUTIONS:
[Your precautions and next steps here]

THINGS TO REMEMBER:
[Your important reminders here]

Be professional, accurate, and empathetic. This is for a real patient who needs proper guidance and keep the report short and easy to understand.
"""
        
        # Generate content
        response = model.generate_content(prompt)
        response_text = response.text
        
        print(f"API Response received successfully")
        
        # Parse the response into sections
        report_data = {
            "description": "",
            "precautions": "",
            "things_to_remember": ""
        }
        
        current_section = None
        section_content = ""
        
        for line in response_text.split('\n'):
            line_upper = line.upper().strip()
            
            if "CLINICAL DESCRIPTION:" in line_upper:
                
                if current_section and section_content:
                    report_data[current_section] = section_content.strip()
                current_section = "description"
                section_content = ""
            elif "RECOMMENDED PRECAUTIONS:" in line_upper:
                if current_section and section_content:
                    report_data[current_section] = section_content.strip()
                current_section = "precautions"
                section_content = ""
            elif "THINGS TO REMEMBER:" in line_upper:
                if current_section and section_content:
                    report_data[current_section] = section_content.strip()
                current_section = "things_to_remember"
                section_content = ""
            elif current_section and line.strip():
                section_content += line + "\n"
        
        
        if current_section and section_content:
            report_data[current_section] = section_content.strip()
        
        
        for section_name, content in report_data.items():
            if not content:
                print(f"  Warning: {section_name} is empty, using fallback")
        
        return report_data
        
    except Exception as e:
        print(f" Gemini API Error: {str(e)}")

#making the report
def generate_pdf_report(patient_info, description, precautions, things_to_remember, output_filename):
    pdf_path = REPORTS_DIR / output_filename
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14
    )
    
    # Title
    story.append(Paragraph("BRAIN TUMOR DETECTION REPORT", title_style))
    story.append(Paragraph("AI-Assisted Medical Analysis", ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=12
    )))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Information Section
    story.append(Paragraph("Patient Information", heading_style))
    
    patient_data = [
        ['Field', 'Details'],
        ['Name', patient_info.get('name', 'N/A')],
        ['Age', str(patient_info.get('age', 'N/A')) + ' years'],
        ['Gender', patient_info.get('gender', 'N/A').capitalize()],
        ['Symptoms', patient_info.get('symptoms', 'Not specified')],
        ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 3.5*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.25*inch))
    
    # AI Prediction Section
    story.append(Paragraph("AI Analysis Results", heading_style))
    
    prediction_data = [
        ['Metric', 'Result'],
        ['Predicted Condition', patient_info.get('prediction', 'N/A').replace('_', ' ').title()],
        ['Confidence Score', f"{patient_info.get('confidence', 0) * 100:.2f}%"],
        ['Analysis Date', datetime.now().strftime('%Y-%m-%d')],
    ]
    
    prediction_table = Table(prediction_data, colWidths=[1.5*inch, 3.5*inch])
    prediction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(prediction_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Clinical Description
    story.append(Paragraph("Clinical Description", heading_style))
    description_cleaned = description.replace('*', '').replace('\n\n', '<br/><br/>').replace('\n', '<br/>')
    story.append(Paragraph(description_cleaned, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Recommended Precautions
    story.append(Paragraph("Recommended Precautions & Next Steps", heading_style))
    precautions_cleaned = precautions.replace('*', '').replace('\n', '<br/>')
    story.append(Paragraph(precautions_cleaned, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Things to Remember
    story.append(Paragraph("Important Things to Remember", heading_style))
    remember_cleaned = things_to_remember.replace('*', '').replace('\n', '<br/>')
    story.append(Paragraph(remember_cleaned, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer/Disclaimer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        leading=11
    )
    
    story.append(Paragraph(
        "<b>MEDICAL DISCLAIMER:</b> This report is generated using AI-assisted analysis and is for informational purposes only. "
        "It should NOT be considered a medical diagnosis. Please consult with qualified healthcare professionals for proper diagnosis, treatment, and medical advice.",
        footer_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "For medical concerns, please consult a qualified neurologist or your primary care physician immediately.",
        footer_style
    ))
    
    # Build PDF
    try:
        doc.build(story)
        print(f" PDF Report generated: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f" PDF generation error: {str(e)}")
        raise


@app.get("/")
async def root():
    return {
        "service": "Report Generator API",
        "version": "2.0.0",
        "llm_provider": "Google Generative AI (Gemini)",
        "endpoints": {
            "generate-content": "POST /generate-content",
            "generate-pdf": "POST /generate-pdf",
            "download": "GET /download/{filename}"
        }
    }


@app.get("/health")
async def health():
    api_status = "configured" if GOOGLE_API_KEY else "not_configured"
    return {
        "status": "healthy",
        "llm_provider": "Google Generative AI",
        "api_key_status": api_status,
        "reports_dir": str(REPORTS_DIR)
    }


@app.post("/generate-content")
async def generate_content(
    prediction: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    symptoms: str = Form(default="Not specified"),
    confidence: float = Form(default=0.85)
):
    try:
        if not GOOGLE_API_KEY:
            raise HTTPException(
                status_code=500, 
                detail="Google API key not configured. Please set GOOGLE_API_KEY in environment variables."
            )
        
        print(f" Generating content for patient: {name}")
        
        patient_info = {
            "name": name,
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "prediction": prediction,
            "confidence": confidence
        }
        
        report_content = generate_report(
            prediction=prediction,
            patient_info=patient_info
        )
        
        return {
            "status": "success",
            "description": report_content.get("description", ""),
            "precautions": report_content.get("precautions", ""),
            "things_to_remember": report_content.get("things_to_remember", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@app.post("/generate-pdf")
async def generate_pdf(
    prediction: str = Form(...),
    confidence: float = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    symptoms: str = Form(...),
    description: str = Form(...),
    precautions: str = Form(...),
    things_to_remember: str = Form(...)
):
    try:
        print(f"📄 Generating PDF report for patient: {name}")
        
        patient_info = {
            "name": name,
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "prediction": prediction,
            "confidence": confidence
        }
        
        pdf_filename = f"report_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        pdf_path = generate_pdf_report(
            patient_info=patient_info,
            description=description,
            precautions=precautions,
            things_to_remember=things_to_remember,
            output_filename=pdf_filename
        )
        
        return {
            "status": "success",
            "pdf_filename": pdf_filename,
            "pdf_path": str(pdf_path)
        }
        
    except Exception as e:
        print(f" PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download generated PDF report
    """
    file_path = REPORTS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


