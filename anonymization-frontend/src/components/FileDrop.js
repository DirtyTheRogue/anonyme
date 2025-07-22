import React from "react";
import { useDropzone } from "react-dropzone";

function FileDrop({ onFileSelect }) {
  const onDrop = (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      style={{
        border: "2px dashed #888",
        padding: "20px",
        textAlign: "center",
        borderRadius: "5px",
        backgroundColor: isDragActive ? "#e3f2fd" : "#f9f9f9",
        cursor: "pointer",
      }}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Déposez vos fichiers ici...</p>
      ) : (
        <p>Glissez et déposez vos fichiers ici, ou cliquez pour sélectionner</p>
      )}
    </div>
  );
}

export default FileDrop;
