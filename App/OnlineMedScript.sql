USE OnlineMed;
--DROP TABLE 
--DROP TABLE TestResult;
--DROP TABLE Test;
--DROP TABLE Patient;
--DROP TABLE Admin;


--CREATE TABLE Admin (
--    AdminId     INT PRIMARY KEY,
--    UserName    VARCHAR(20)
--);

--INSERT INTO Admin
--VALUES (1, 'Yuna Ukawa');
--SELECT * FROM Admin;

CREATE TABLE [dbo].[Patient] (
    [PatientID]   INT          NOT NULL,
    [FirstName]   VARCHAR (50) NULL,
    [LastName]    VARCHAR (50) NULL,
    [DateOfBirth] DATE         NULL,
    [Gender]      CHAR (1)     NULL,
    PRIMARY KEY CLUSTERED ([PatientID] ASC)
);
INSERT INTO Patient VALUES
(20000001, 'Yuna', 'Ukawa', '2000-01-01', 'f');
SELECT * FROM Patient;

CREATE TABLE [dbo].[Test] (
    [TestID]      INT           NOT NULL,
    [TestName]    VARCHAR (100) NULL,
    [Description] TEXT          NULL,
    [NormalRange] VARCHAR (100) NULL,
    [Unit]        VARCHAR (10)  NULL,
    PRIMARY KEY CLUSTERED ([TestID] ASC)
);
INSERT INTO Test VALUES 
(1, 'Glucose', 'Blood sugar level', '70-99', 'mg/dL'),
(2, 'White Blood Cell Count', 'Measures the number of white blood cells in blood', '4.5-11.0', 'K/µL'),
(3, 'Red Blood Cell Count', 'Measures the number of red blood cells in blood', '4.2-5.9', 'M/µL'),
(4, 'Hemoglobin', 'Oxygen-carrying protein in red blood cells', '13.8-17.2', 'g/dL'),
(5, 'Hematocrit', 'Percentage of red blood cells in blood', '40.7-50.3', '%'),
(6, 'Cholesterol', 'Total cholesterol level', '125-200', 'mg/dL'),
(7, 'Triglycerides', 'Type of fat in the blood', '0-150', 'mg/dL'),
(8, 'HDL Cholesterol', 'Good cholesterol level', '40-60', 'mg/dL'),
(9, 'LDL Cholesterol', 'Bad cholesterol level', '0-100', 'mg/dL'),
(10, 'Vitamin D', 'Vitamin D level', '20-50', 'ng/mL'),
(11, 'Calcium', 'Calcium level', '8.6-10.2', 'mg/dL'),
(12, 'Iron', 'Iron level', '60-170', 'ug/dL'),
(13, 'Potassium', 'Potassium level', '3.5-5.2', 'mmol/L'),
(14, 'Sodium', 'Sodium level', '135-145', 'mmol/L'),
(15, 'TSH', 'Thyroid stimulating hormone level', '0.5-4.0', 'uIU/mL'),
(16, 'ALT', 'Liver enzyme test', '7-56', 'units/L'),
(17, 'AST', 'Liver enzyme test', '10-40', 'units/L'),
(18, 'Total Protein', 'Total protein level', '6.0-8.3', 'g/dL'),
(19, 'Total Bilirubin', 'Total protein level', '0.3-1.2', 'mg/dL');
SELECT * FROM Test;

CREATE TABLE [dbo].[PatientTest] (
    [PatientTestID] INT  NOT NULL,
    [PatientID]     INT  NOT NULL,
    [TestDate]      DATE NOT NULL,
    [Comments]      TEXT NULL,
    CONSTRAINT [PK_PatientTest] PRIMARY KEY CLUSTERED ([PatientTestID] ASC),
    CONSTRAINT [FK_PatientTest_PatientID] FOREIGN KEY ([PatientID]) REFERENCES [dbo].[Patient] ([PatientID])
);


CREATE TABLE [dbo].[TestResult] (
    [ResultID]      INT             NOT NULL,
    [PatientTestID] INT             NULL,
    [PatientID]     INT             NOT NULL,
    [TestID]        INT             NULL,
    [TestDate]      DATE            NULL,
    [ResultValue]   DECIMAL (10, 2) NULL,
    PRIMARY KEY CLUSTERED ([ResultID] ASC),
    CONSTRAINT [FK_TestResult_PatientID] FOREIGN KEY ([PatientID]) REFERENCES [dbo].[Patient] ([PatientID]),
    CONSTRAINT [FK_TestResult_PatientTestID] FOREIGN KEY ([PatientTestID]) REFERENCES [dbo].[PatientTest] ([PatientTestID]),
    CONSTRAINT [FK_TestResult_TestID] FOREIGN KEY ([TestID]) REFERENCES [dbo].[Test] ([TestID])
);
SELECT * FROM TestResult;

CREATE TABLE [dbo].[ImagePath] (
    [ImageID]          INT           NOT NULL,
    [ImageDescription] VARCHAR (255) NULL,
    [ImagePath]        VARCHAR (255) NOT NULL,
    [PatientID]        INT           NULL,
    [PatientTestID]    INT           NULL,
    CONSTRAINT [PK_ImagePath] PRIMARY KEY CLUSTERED ([ImageID] ASC),
    CONSTRAINT [FK_ImagePath_PatientID] FOREIGN KEY ([PatientID]) REFERENCES [dbo].[Patient] ([PatientID]),
    CONSTRAINT [FK_ImagePath_PatientTestID] FOREIGN KEY ([PatientTestID]) REFERENCES [dbo].[PatientTest] ([PatientTestID])
);
SELECT * FROM ImagePath;
