        // Product Database (for demo)
        // const products = {};

        // Shopping Cart
        let cart = [];
        let selectedPaymentMethod = 'cash';
        // const scanner = new Html5Qrcode("scanner");
        // DOM Elements
        const barcodeInput = document.getElementById('barcodeInput');
        const cartItems = document.getElementById('cartItems');
        const itemCount = document.getElementById('itemCount');
        const cartTotal = document.getElementById('cartTotal');

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Load cart from session
            const savedCart = sessionStorage.getItem('cashierCart');
            if (savedCart) {
                cart = JSON.parse(savedCart);
                updateCartDisplay();
            }
            
            // Enter key to scan
            barcodeInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    scanProduct();
                }
            });
            
            // Focus scanner
            focusScanner();
            
            // Update date time
            updateDateTime();
            setInterval(updateDateTime, 60000); // Update every minute
        });

        // Update date time display
        function updateDateTime() {
            const now = new Date();
            const dateStr = now.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
            const timeStr = now.toLocaleTimeString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit'
            });
            document.getElementById('currentDateTime').textContent = `${dateStr} | ${timeStr}`;
        }


// function focusScanner() {
//     console.log("start")
//     scanner.start(
//         { facingMode: "environment" },   // uses main cam if available
//         {
//             fps: 25,

//             // 🔥 MUST be wide and thin for 1D barcode
//             qrbox: {
//                 width: 400,
//                 height: 120
//             },

//             // 🎯 Barcode formats only
//             formatsToSupport: [
//                 Html5QrcodeSupportedFormats.CODE_128,
//                 Html5QrcodeSupportedFormats.EAN_13,
//                 Html5QrcodeSupportedFormats.UPC_A,
//                 Html5QrcodeSupportedFormats.CODE_39
//             ],

//             experimentalFeatures: {
//                 useBarCodeDetectorIfSupported: true
//             }
//         },
//         (code) => {
//             console.log("Scanned:", code);

//             barcodeInput.value = code;
//             scanProduct();
//             // stopScanner();
//         },
//         () => {}
//     );
// }

// function stopScanner() {
//     if (scanner.isScanning) {
//         scanner.stop();
//     }
// }


let codeReader = null;

function focusScanner() {

    if (!codeReader) {
        codeReader = new ZXing.BrowserMultiFormatReader();
    }

    const videoElement = document.getElementById("scanner");
    videoElement.style.display = "block";

    codeReader.decodeFromVideoDevice(null, videoElement, (result, error) => {

        if (result) {
            console.log("Barcode:", result.text);

            barcodeInput.value = result.text;
            scanProduct();

            // stopScanner();   // stop after success
        }

        if (error && !(error instanceof ZXing.NotFoundException)) {
            console.error(error);
        }
    });
}

function stopScanner(){
    if(codeReader){
        codeReader.reset();
    }
}


// function stopScanner(){
//     scanner.stop()
//     .then(() => {
//         console.log("Scanner stopped, camera released.");
//     })
//     .catch(err => {
//         console.error("Failed to stop scanner:", err);
//     });
// }


        // Focus scanner input
function scanProduct() {
    const barcode = barcodeInput.value.trim();

    if (!barcode) {
        alert('Please enter a barcode!');
        return;
    }

   fetch(`/dashboard/enterbarcode/?barcode=${barcode}`)
   .then(res=>res.json())
   .then(product=>{
        addToCart(product);
        updateProductDetails(product);
        barcodeInput.value = '';

        console.log(product)
   }).catch(err=>{
    console.log(err)
   })
}





        // Add product to cart
        function addToCart(product) {
            // Check if product already in cart
            const existingItem = cart.find(item => item.id === product.id);
            
            if (existingItem) {
                if (existingItem.quantity >= product.stock) {
                    alert(`Only ${product.stock} units available!`);
                    return;
                }
                existingItem.quantity += 1;
            } else {
                if (product.stock <= 0) {
                    alert('Product out of stock!');
                    return;
                }
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1,
                    tax: product.tax,
                    barcode: product.barcode,
                    stock: product.stock,
                    // icon: product.icon
                });
            }
            // Save to session
            sessionStorage.setItem('cashierCart', JSON.stringify(cart));
            
            // Update display
            updateCartDisplay();
            updatePaymentSummary();
        }

        // Update cart display
        function updateCartDisplay() {
            // Update item count
            const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
            itemCount.textContent = `${totalItems} item${totalItems !== 1 ? 's' : ''}`;
            
            // Update cart total
            const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            cartTotal.textContent = `Rs${total}`;
            
            // Display cart items
            if (cart.length === 0) {
                cartItems.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">
                            <i class="fas fa-shopping-cart"></i>
                        </div>
                        <h3>Your cart is empty</h3>
                        <p>Scan products to add them to cart</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            cart.forEach((item, index) => {
                const itemTotal = item.price * item.quantity;
                    // <div class="item-icon">${item.icon}</div> place on inside html

                html += `
                    <div class="cart-item">
                        <div class="item-details">
                            <div class="item-name">${item.name}</div>
                            <div class="item-price">Rs${item.price} each</div>
                        </div>
                        <div class="quantity-controls">
                            <button class="qty-btn" onclick="changeQuantity(${index}, -1)">-</button>
                            <span class="item-qty">${item.quantity}</span>
                            <button class="qty-btn" onclick="changeQuantity(${index}, 1)">+</button>
                        </div>
                        <div class="item-total">Rs${itemTotal}</div>
                        <button class="remove-btn" onclick="removeItem(${index})" title="Remove">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
            });
            
            cartItems.innerHTML = html;
        }

        // Change item quantity
        function changeQuantity(index, change) {
            const item = cart[index];
            const newQty = item.quantity + change;
            
            if (newQty < 1) {
                removeItem(index);
                return;
            }
            
            if (newQty > item.stock) {
                alert(`Only ${item.stock} units available!`);
                return;
            }
            
            item.quantity = newQty;
            sessionStorage.setItem('cashierCart', JSON.stringify(cart));
            updateCartDisplay();
            updatePaymentSummary();
        }

        // Remove item from cart
        function removeItem(index) {
            if (confirm('Remove this item from cart?')) {
                cart.splice(index, 1);
                sessionStorage.setItem('cashierCart', JSON.stringify(cart));
                updateCartDisplay();
                updatePaymentSummary();
                
                if (cart.length === 0) {
                    clearProductDetails();
                }
            }
        }

        // Clear entire cart
        function clearCart() {
            if (cart.length === 0) {
                alert('Cart is already empty!');
                return;
            }
            
            if (confirm('Clear all items from cart?')) {
                cart = [];
                sessionStorage.removeItem('cashierCart');
                updateCartDisplay();
                clearProductDetails();
                updatePaymentSummary();
                alert('Cart cleared!');
            }
        }

        // Update product details display
        function updateProductDetails(product) {
            document.getElementById('productName').textContent = product.name;
            document.getElementById('productBarcode').textContent = product.barcode;
            document.getElementById('productPrice').textContent = `${product.price}`;
            document.getElementById('productStock').textContent = product.stock;
            document.getElementById('productTax').textContent = `${product.tax}%`;
            document.getElementById('productCategory').textContent = product.category;
            
            // Update stock status badge
            const statusBadge = document.getElementById('stockStatus');
            statusBadge.className = 'stock-badge ';
            if (product.stock > 20) {
                statusBadge.classList.add('stock-good');
                statusBadge.textContent = 'In Stock';
            } else if (product.stock > 0) {
                statusBadge.classList.add('stock-low');
                statusBadge.textContent = 'Low Stock';
            } else {
                statusBadge.classList.add('stock-out');
                statusBadge.textContent = 'Out of Stock';
            }
            
            // Update product icon
            // document.getElementById('productIcon').innerHTML = product.icon;
        }

        // Clear product details
        function clearProductDetails() {
            document.getElementById('productName').textContent = 'No Product Selected';
            document.getElementById('productBarcode').textContent = '-';
            document.getElementById('productPrice').textContent = '$0.00';
            document.getElementById('productStock').textContent = '0';
            document.getElementById('productTax').textContent = '0%';
            document.getElementById('productCategory').textContent = '-';
            document.getElementById('stockStatus').className = 'stock-badge stock-good';
            document.getElementById('stockStatus').textContent = 'In Stock';
            document.getElementById('productIcon').innerHTML = '<i class="fas fa-cube"></i>';
        }

        // Update payment summary
        function updatePaymentSummary() {
            let subtotal = 0;
            let tax = 0;
            
            cart.forEach(item => {
                const itemTotal = item.price * item.quantity;
                subtotal += itemTotal;
                tax += itemTotal * (item.tax / 100);    
            });
            console.log(cart)
            const discount = 0; // Can add discount logic
            const total = subtotal + tax - discount;
            
            document.getElementById('subtotalAmount').textContent = `Rs${subtotal}`;
            document.getElementById('taxAmount').textContent = `Rs${tax}`;
            document.getElementById('discountAmount').textContent = `Rs${discount}`;
            document.getElementById('totalAmount').textContent = `Rs${total}`;
        }

        // Select payment method
        function selectPaymentMethod(element, method) {
            // Remove selected class from all
            document.querySelectorAll('.method-option').forEach(el => {
                el.classList.remove('selected');
            });
            
            // Add to clicked element
            element.classList.add('selected');
            selectedPaymentMethod = method;
        }

        // Process payment
        function processPayment() {
            if (cart.length === 0) {
                alert('Add items to cart before processing payment!');
                return;
            }
            
            const total = document.getElementById('totalAmount').textContent;
            const invoiceNumber = 'INV-' + Date.now().toString().slice(-6);
            
            // Generate receipt
            generateReceipt(invoiceNumber);
            
            // Show confirmation
            if (confirm(`Process ${selectedPaymentMethod.toUpperCase()} payment of ${total}?\n\nInvoice: ${invoiceNumber}`)) {
                // Process payment (in real app, this would call backend)
                setTimeout(() => {
                    alert(`Payment processed successfully!\n\nInvoice: ${invoiceNumber}\nMethod: ${selectedPaymentMethod}\nAmount: ${total}\n\nReceipt has been printed.`);
                    
                    // Clear cart after successful payment
                    cart = [];
                    sessionStorage.removeItem('cashierCart');
                    updateCartDisplay();
                    clearProductDetails();
                    updatePaymentSummary();
                    
                    // Hide receipt preview
                    document.getElementById('receiptPreview').style.display = 'none';
                    
                }, 500);
            }
        }

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;



        // Generate receipt preview
            function generateReceipt(invoiceNumber) {
                const now = new Date();
                const dateStr = now.toLocaleDateString();
                const timeStr = now.toLocaleTimeString();
                
                // Update receipt header
                document.getElementById('receiptDate').textContent = `${dateStr} ${timeStr}`;
                document.getElementById('receiptInvoice').textContent = `Invoice: ${invoiceNumber}`;
                
                // Add items to receipt
                let receiptHTML = '';
                let subtotal = 0;
                let tax = 0;
                cart.forEach(item => {
                    const itemTotal = item.price * item.quantity;
                    const itemTax = itemTotal * (item.tax / 100);
                    subtotal += itemTotal;
                    tax += itemTax;
                    
                    receiptHTML += `
                        <div style="display: flex; justify-content: space-between; margin: 2px 0;">
                            <span>${item.name} x${item.quantity}</span>
                            <span>Rs${itemTotal}</span>
                        </div>
                    `;
                });
                
                const total = subtotal + tax;
                
                receiptHTML += `
                    <div style="border-top: 1px dashed #ccc; margin: 5px 0; padding-top: 5px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>Subtotal:</span>
                            <span>Rs${subtotal}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Tax:</span>
                            <span>Rs${tax}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-weight: bold; border-top: 1px solid #ccc; padding-top: 3px; margin-top: 3px;">
                            <span>TOTAL:</span>
                            <span>Rs${total}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span>Payment:</span>
                            <span>${selectedPaymentMethod.toUpperCase()}</span>
                        </div>
                    </div>
                `;
                
                document.getElementById('receiptItems').innerHTML = receiptHTML;
                document.getElementById('receiptPreview').style.display = 'block';

                fetch("/dashboard/checkout/",{
                    method:"POST",
                    headers:{
                        'content-type':"application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body:JSON.stringify({
                        invoic:invoiceNumber,
                        subtotal:subtotal,
                        tax:tax,
                        total:total,
                        payment_method:selectedPaymentMethod,
                        cart: cart.map(item => ({
                        product_id:item.id,
                        barcode: item.barcode,
                        price: item.price,
                        quantity: item.quantity,
                        tax: item.tax
                    }))
                    })

                })
                .then(res=>res.json())
                .then(data=>{
                    if(data.status === 'success'){
                        console.log("data save!")

                    }
                    else{
                        console.log("cart",cart)

                    }
                })

            }

        // Initialize payment summary
        updatePaymentSummary();