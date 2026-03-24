<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        if (!Schema::hasTable('product_pricing_tiers')) {
            Schema::create('product_pricing_tiers', function (Blueprint $table) {
                $table->id();
                $table->foreignId('product_id')->constrained()->onDelete('cascade');
                $table->integer('quantity'); // Pricing beak (e.g., 3)
                $table->decimal('price', 10, 2); // Total price for that quantity (e.g., 100.00)
                $table->string('name')->nullable(); // Optional label (e.g., "Wholesale")
                $table->timestamps();
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('product_pricing_tiers');
    }
};
