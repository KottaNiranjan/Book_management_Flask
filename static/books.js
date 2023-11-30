document.addEventListener('DOMContentLoaded', function () {
    // Fetch and display books on page load
    fetchBooks();

    // Add event listeners for form submissions
    document.getElementById('add-book-form').addEventListener('submit', function (e) {
        e.preventDefault();
        addBook();
    });

    document.getElementById('update-book-form').addEventListener('submit', function (e) {
        e.preventDefault();
        updateBook();
    });

    document.getElementById('delete-book-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const book_id=document.getElementById("deleteBookId").value
        deleteBook(book_id);
    });
});



function fetchBooks() {
    
    fetch('/books')
        .then(response => response.json())
        .then(books => {
            const booksList = document.getElementById('books-list');
            booksList.innerHTML = '';

            if (books.length > 0) {
                
                const table = document.createElement('table');
                table.classList.add('table', 'table-bordered', 'table-striped','table-hover');

               
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                ['id','Title', 'Author', 'Genre', 'Publication Year'].forEach(column => {
                    const th = document.createElement('th');
                    th.textContent = column;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                
                const tbody = document.createElement('tbody');
                books.forEach(book => {
                    const row = document.createElement('tr');
                    ['id','title', 'author', 'genre', 'publication_year'].forEach(property => {
                        const cell = document.createElement('td');
                        cell.textContent = book[property];
                        row.appendChild(cell);
                    });
                    tbody.appendChild(row);
                });
                table.appendChild(tbody);

                
                booksList.appendChild(table);
            } else {
                // Display a message if there are no books
                booksList.innerHTML = '<p>No books available</p>';
            }
        })
        .catch(error => {console.error('Error fetching books:', error)});
}


function addBook(){
    fetch("/access_token").then(response=>response.json()).then(data=>{
        const token=String(data)
    fetch("/add_books",{
        method:"POST",
        headers:{
            'Content-Type':'application/JSON',
            'auth':`${token}`
        },
        body:JSON.stringify({
            'id':document.getElementById('id').value,
            'title':document.getElementById('title').value,
            'author':document.getElementById('author').value,
            'genre' : document.getElementById('genre').value,
            'publication_year'  : document.getElementById('publicationYear').value
            
        }),
    })
    .then(response=>{
        if(response.ok){
            return response.json()
        }
        else{
            throw new Error("Failed to Add Data")
        }
    }
    )
    .then(data=>{
        if ('error' in data){
            alert(data['error'])
            throw new Error(data['error'])
        }

        fetchBooks();
        // Clear the form fields
        console.log(data)
        document.getElementById('id').value='';
        document.getElementById('title').value = '';
        document.getElementById('author').value = '';
        document.getElementById('genre').value = '';
        document.getElementById('publicationYear').value = '';
        const updateMessage = document.getElementById('update-message');
    updateMessage.style.display = 'block';
        document.getElementById("status").innerHTML="Book added Successfully See the Books List"
    // Optionally, hide the message after a few seconds
    setTimeout(() => {
        updateMessage.style.display = 'none';
    }, 4500);
    })
    .catch(error=>{
        console.log("Error adding book",error)
    
    })
})
}

function deleteBook(book_id){
    fetch("/access_token").then(response=>response.json()).then(data=>{
        const token=String(data)
     
    fetch(`/delete_book/${book_id}`,{
        method:'DELETE',
        headers:{
            'Content-Type':'application/JSON',
            'auth':`${token}`
        }
    })
    .then(response=>{
        if(response.ok){
            return response.json()
        }
        else{
            throw new Error("Key Not Found")
        }
    })
    .then(data=>{
        if ('error' in data){
            alert(data['error'])
            throw new Error()
        }
        console.log(data)
        fetchBooks();

        document.getElementById("deleteBookId").value=""
        const updateMessage = document.getElementById('update-message');
        
    updateMessage.style.display = 'block';
    document.getElementById("status").innerHTML="Book deleted Successfully See the Books List"

    // Optionally, hide the message after a few seconds
    setTimeout(() => {
        updateMessage.style.display = 'none';
    }, 3000);

    })
    .catch(error=>{
        console.log("Error adding book",error)
    })
    
})
}

function updateBook(){
    fetch("/access_token").then(response=>response.json()).then(data=>{
        const token=String(data)

    const bookId = document.getElementById('updateBookId').value;
    const title = document.getElementById('updateTitle').value;
    const author = document.getElementById('updateAuthor').value;
    const genre = document.getElementById('updateGenre').value;
    const publication_year = document.getElementById('updatePublicationYear').value;
    s={"title":title,"author":author,"genre":genre,"publication_year":publication_year}
    ele={}
   
    for(const element in s){
        console.log(element)
        if (s[element].length!=0){
            ele[element]=s[element]
        }
    };
    len=Object.keys(ele).length
   
    if (len==0){
        alert("Enter details")
        throw new Error("Enter details")
    }
   fetch(`/update_book/${bookId}`,{
    method:'PUT',
    headers:{
        'Content-Type':'application/JSON',
        'auth':`${token}`
    },
    body:JSON.stringify(ele)
   })
   .then(response=>{
    if(response.ok){
        return response.json()
    }
    else{
        throw new Error("Book is not updated")
    }
})
.then(data=>{
    
    if ('error' in data){
        alert(data['error'])
        throw new Error()
    }

    fetchBooks()
   document.getElementById('updateBookId').value="";
   document.getElementById('updateTitle').value="";
    document.getElementById('updateAuthor').value="";
    document.getElementById('updateGenre').value="";
    const updateMessage = document.getElementById('update-message');
    
    updateMessage.style.display = 'block';
    document.getElementById("status").innerHTML="Book is updated Successfully See the Books List"

    setTimeout(() => {
        updateMessage.style.display = 'none';
    }, 3000);
}).catch(error=>{
    console.log(error)
})
})
}
