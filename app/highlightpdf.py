from PyPDF2 import PdfFileWriter, PdfFileReader


######################### called from Meetingvalidation ##########################################
def HighlightAMeetingInPDF(meetingrecord,pathofinputpdf):
	pdfInput = PdfFileReader(open(pathofinputpdf, "rb"))	#"/home/grad05/rubya001/AAmeeting/output.pdf"
	pdfOutput = PdfFileWriter()

	page1 = pdfInput.getPage(int(meetingrecord[10].split("_")[0]))							#pdfInput.getPage(0)
	
	#day
	'''x_day=meetingrecord[5].split('||')[0]
	y_day=meetingrecord[6].split('||')[0]
	w_day=meetingrecord[7].split('||')[0]
	h_day=meetingrecord[8].split('||')[0]
	highlight_day = createHighlight(   x_day,y_day,w_day,h_day, {			#100, 400, 400, 500,
	    "author": "",
	    "contents": "day"
	})

	addHighlightToPage(highlight_day, page1, pdfOutput)'''
	
	#time
	x_time=meetingrecord[5].split('||')[1]
	y_time=meetingrecord[6].split('||')[1]
	w_time=meetingrecord[7].split('||')[1]
	h_time=meetingrecord[8].split('||')[1]
	highlight_time = createHighlight(   x_time,y_time,w_time,h_time, {			#100, 400, 400, 500,
	    "author": "",
	    "contents": "time"
	})

	addHighlightToPage(highlight_time, page1, pdfOutput)


	#address
	'''x_addr=meetingrecord[5].split('||')[2]
	y_addr=meetingrecord[6].split('||')[2]
	w_addr=meetingrecord[7].split('||')[2]
	h_addr=meetingrecord[8].split('||')[2]
	highlight_addr = createHighlight(   x_addr,y_addr,w_addr,h_addr, {			#100, 400, 400, 500,
	    "author": "",
	    "contents": "address"
	})

	addHighlightToPage(highlight_addr, page1, pdfOutput)'''

	pdfOutput.addPage(page1)

	outputStream = open("/home/grad05/rubya001/AAmeeting/aa-crowdsource/output2.pdf", "wb")
	pdfOutput.write(outputStream)

	return "/home/grad05/rubya001/AAmeeting/aa-crowdsource/output2.pdf"


from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    TextStringObject,
    ArrayObject
)

# x1, y1 starts in bottom left corner
def createHighlight(x1, y1, x2, y2, meta, color = [1, 0, 0]):
    newHighlight = DictionaryObject()

    newHighlight.update({
        NameObject("/F"): NumberObject(4),
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Highlight"),

        NameObject("/T"): TextStringObject(meta["author"]),
        NameObject("/Contents"): TextStringObject(meta["contents"]),

        NameObject("/C"): ArrayObject([FloatObject(c) for c in color]),
        NameObject("/Rect"): ArrayObject([
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y2)
        ]),
        NameObject("/QuadPoints"): ArrayObject([
            FloatObject(x1),
            FloatObject(y2),
            FloatObject(x2),
            FloatObject(y2),
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y1)
        ]),
    })

    return newHighlight

def addHighlightToPage(highlight, page, output):
    highlight_ref = output._addObject(highlight);

    if "/Annots" in page:
        page[NameObject("/Annots")].append(highlight_ref)
    else:
        page[NameObject("/Annots")] = ArrayObject([highlight_ref])
